"""
    C&M - Socket Live Tweets
    ========================
    Gestor del Stream Tweets servicio Twitter API
    :autor @cmorocho
"""
import json
import requests
import logging
from math import inf
from time import sleep
from threading import Thread
from flask import request
from flask_socketio import SocketIO, disconnect
from cm_gestores import gestor_tweets as gt
from cm_gestores import gestor_usuario as gu
from common_utils import bearer_oauth, get_nombre_tipo
log = logging.getLogger(__name__)


class TweetLiveCM(SocketIO):
    """
        Listener Stream Tweets
    """
    # Diccionario de Cuentas
    cuentas = {}
    # URLs api twitter
    url_stream = "https://api.twitter.com/2/tweets/search/stream"
    # Atributos a Obtener
    fileds_get = "tweet.fields=created_at,referenced_tweets,entities&expansions=author_id," \
                 "referenced_tweets.id.author_id&user.fields=profile_image_url,verified"

    def __init__(self, app, max_retries=inf):
        self.cm_app = app
        super(TweetLiveCM, self).__init__(app)

        # Inicia el Stream
        self.running = False
        self.max_retries = max_retries
        self.thread = Thread(target=self.run_live_stream, name="CM Tweet Stream")
        self.thread.start()

        # Registro de Eventos del Socket
        self.on_event('connect', self.connect_live)
        self.on_event("disconnect", self.disconnect_live)

    def connect_live(self):
        # Valida el User Token
        user = request.sid
        print("--CONECTADO: ", user)
        token = request.values.get('token')
        cuenta = request.values.get('cuenta')
        # Valida el token y la cuenta
        if token:
            # Conecta al usuario al strem live
            self.join_tweet_live(cuenta, user)
        else:
            # Desconecta al usuario
            disconnect(user)

    def disconnect_live(self):
        user = request.sid
        print("-- DESCONECTADO", user)
        cuentas = self.get_cuentas_user(user)
        for cuenta in cuentas:
            self.leave_tweet_live(cuenta, user)

    def get_cuentas_user(self, usuario):
        return list(filter(lambda c: usuario in self.cuentas[c], self.cuentas.keys()))

    def join_tweet_live(self, cuenta, usuario):
        if self.cuentas.get(cuenta):
            self.cuentas[cuenta].add(usuario)
        else:
            self.cuentas[cuenta] = {usuario}

    def leave_tweet_live(self, cuenta, usuario):
        try:
            if self.cuentas.get(cuenta):
                self.cuentas[cuenta].remove(usuario)
            if len(self.cuentas[cuenta]) == 0:
                self.cuentas.pop(cuenta)
        except KeyError:
            pass

    def run_live_stream(self):
        self.running = True
        stall_timeout = 90
        http_error_wait = 3000
        while self.running:
            print("STREAM INICIADO")
            try:
                with requests.get(f"{self.url_stream}?{self.fileds_get}", auth=bearer_oauth, timeout=stall_timeout,
                                  stream=True) as resp:
                    if resp.status_code == 200:
                        for line_response in resp.iter_lines(decode_unicode=True):
                            if line_response:
                                self.on_data(json.loads(line_response))
                            else:
                                log.error(f"Live stream (HTTP {resp.status_code}): Keep Alive")
                            if not self.running:
                                break
                    else:
                        log.error(f"Live stream (HTTP {resp.status_code}): {resp.text}")
                        if not self.running:
                            break
                        sleep(http_error_wait)
            except Exception as e:
                log.error(f"Live stream ({str(e)})")
                if not self.running:
                    break
                sleep(http_error_wait)

    def on_data(self, tweet):
        """
        Procesa la informacion del Tweet
        :param tweet:
        :return:
        """
        print("DATA", tweet)
        data = tweet.get("data")
        # Obtiene los datos
        autor_id = data.get("author_id")
        entities = data.get("entities", [])
        referenced = data.get("referenced_tweets", [])
        users = tweet.get("includes", {}).get("users", [])
        tweets = tweet.get("includes", {}).get("tweets", [])
        autor = next(filter(lambda u: u['id'] == autor_id, users))
        # Arma la data Tweet
        data_tweet = {
            'codigo': data.get("id"),
            'activo': True,
            'autor_id': autor_id,
            'fecha': data.get('created_at'),
            'texto': data.get("text"),
            'usuario': {
                'nombre': autor.get("name"),
                'verified': autor.get("verified"),
                'username': autor.get('username'),
                'url_profile': autor.get('profile_image_url'),
            },
            'entidades': self.get_entidades(entities),
        }
        # Emite el Tweet
        cuentas = list(filter(lambda u: u['id'] != autor_id, users))
        cuentas_to_save = self.get_tipo_tweet(referenced, tweets, [c['id'] for c in cuentas])
        # Clasifica el texto segun la Cuenta
        self.clasificar_tweet(cuentas_to_save, data_tweet)

    def emitir_tweet(self, cuentas, data_tweet):
        # Obtiene las Cuentas
        cuentas_old = set(cuentas.keys()).intersection(self.cuentas.keys())
        # Emite el Tweet a todas las cuentas
        for cuenta in cuentas_old:
            tweet = {**data_tweet, **cuentas[cuenta]}
            self.emit(cuenta, tweet)
            data_tweet_user = {'usuario': tweet['usuario'], 'tipo': get_nombre_tipo(tweet['tipo'])}
            self.emit(f"{cuenta}-iteraccion", data_tweet_user)

    def clasificar_tweet(self, cuentas, data_tweet):
        # Guarda el Tweet
        with self.cm_app.app_context():
            c_clases = gu.obtener_clases_cuentas(None, list(cuentas.keys()), '1')
        for cuenta in cuentas:
            clases = [c for c in c_clases.get(cuenta, []) if c['default']]
            if clases:
                cuentas[cuenta]['clasificaciones'] = [self.get_clase_default(clases[0])]
        texto_normalizado = self.cm_app.cm_clasificador.normalizar(data_tweet.get("texto"))
        print("TEXTO NORMALIZADO: ", texto_normalizado)
        if texto_normalizado:  # Valida que haya texto
            for cuenta in cuentas:
                tipo = cuentas[cuenta]['tipo']
                clases = [c for c in c_clases.get(cuenta, []) if not c['default']]
                if tipo != 'RT' and clases:
                    clasificacion = self.cm_app.cm_clasificador.clasificar(texto_normalizado, clases)
                    if clasificacion:
                        cuentas[cuenta]['clasificaciones'] = clasificacion
        print("PREDICCION: ", cuentas)
        # Guarda el tweet
        with self.cm_app.app_context():
            gt.guardar_tweet(data_tweet, cuentas)
        # Emite el tweet
        self.emitir_tweet(cuentas, data_tweet)

    @staticmethod
    def get_tipo_tweet(referenced, tweets, cuentas):
        c_cuentas = {c: {'tipo': 'M', 'origen': ''} for c in cuentas}
        for ref in referenced:
            tweet = next(filter(lambda r: r['id'] == ref['id'], tweets), None)
            if tweet:
                if ref['type'] == "quoted":
                    tipo = 'QT'
                elif ref['type'] == "replied_to":
                    tipo = 'R'
                else:
                    tipo = 'RT'
                c_cuentas[tweet['author_id']] = {'tipo': tipo, 'origen': ref['id']}
        # Retrona el tipo de tweet
        return c_cuentas

    @staticmethod
    def get_entidades(entidades):
        _entidades = {}
        urls = entidades.get("urls", [])
        for url in urls:
            _entidades[url["url"]] = {
                'tipo': 'url',
                'valor': url.get("display_url"),
            }
        mentions = entidades.get("mentions", [])
        for mention in mentions:
            _entidades[f"@{mention['username']}"] = {
                'tipo': 'mention',
                'valor': f"https://twitter.com/{mention['username']}",
            }
        hastags = entidades.get("hashtags", [])
        for hastag in hastags:
            _entidades[f"#{hastag['tag']}"] = {
                'tipo': 'hashtag',
                'valor': f"https://twitter.com/hashtag/{hastag['tag']}",
            }
        annotations = entidades.get("annotations", [])
        for annotation in annotations:
            _entidades[annotation["normalized_text"]] = {
                'tipo': "annotation",
                'valor': annotation["type"],
            }
        # Retorna las entidades
        return [{'label': key, **valor} for key, valor in _entidades.items()]

    @staticmethod
    def get_clase_default(clase):
        return {"clase": clase,  'score': 100, 'is_selected': True}
