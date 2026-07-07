"""
    C&M - Gestor Tweets
    =====================
    Logica para la gestion de tweets
    :autor @cmorocho
"""
import logging
from datetime import date, datetime, timedelta
import requests
from sqlalchemy import func, desc, case, and_
from collections import defaultdict
from sqlalchemy.orm import load_only, contains_eager
from cm_gestores import gestor_usuario
from cm_modelos.modelo_tweets import Tweet, EntidadTweet, ClaseTweet, CuentaTweet
from cm_modelos.modelo_usuario import CuentaClase
from common_utils import objects_as_dict, get_database_session, bearer_oauth, human_format, get_nombre_tipo
from settings import URL_API_TWITTER, MAX_FILAS_POR_PAGINA, FORMAT_DATE
from sqlalchemy_paginator import Paginator

log = logging.getLogger(__name__)
url_tweets_metric = f"{URL_API_TWITTER}/tweets?tweet.fields=public_metrics"


def obtener_total_valores(id_cuenta):
    """
    Obtiene el total de tweets clasificados, mensiones y respuestas
    :param id_cuenta:
    :return:
    """
    session = get_database_session()

    # Obtiene el total de Tweets
    condition_id = CuentaTweet.cuenta_id == id_cuenta
    total_c = count_clasificaciones(session, condition_id)[0]
    condition_m = and_(CuentaTweet.tipo == 'M', condition_id)
    total_m = count_respuestas_mensiones(session, condition_m)[0]
    condition_r = and_(CuentaTweet.tipo == 'R', condition_id)
    total_r = count_respuestas_mensiones(session, condition_r)[0]
    condition_qt = and_(CuentaTweet.tipo == 'QT', condition_id)
    total_qt = count_respuestas_mensiones(session, condition_qt)[0]
    condition_rt = and_(CuentaTweet.tipo == 'RT', condition_id)
    total_rt = count_respuestas_mensiones(session, condition_rt)[0]

    # Obtiene el total de Tweets de este mes
    condition_date = func.to_char(Tweet.fecha, 'YYYY-MM') == date.today().strftime("%Y-%m")
    condition_c = and_(condition_id, condition_date)
    total_mes_c = count_clasificaciones(session, condition_c)[0]

    return {
        'C': {'total': human_format(total_c), 'total_mes': human_format(total_mes_c)},
        'M': {'total': human_format(total_m), 'total_mes': 0},
        'R': {'total': human_format(total_r), 'total_mes': 0},
        'QT': {'total': human_format(total_qt), 'total_mes': 0},
        'RT': {'total': human_format(total_rt), 'total_mes': 0}
    }


def count_clasificaciones(session, condition):
    query_clase = session.query(ClaseTweet.tweet_cuenta_id) \
        .join(CuentaClase, CuentaClase.id == ClaseTweet.cuenta_clase_id)\
        .distinct(ClaseTweet.tweet_cuenta_id)\
        .filter(ClaseTweet.is_selected.is_(True), CuentaClase.activo.is_(True),).subquery('query_tweet')
    query = session.query(func.count(Tweet.id)) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .join(query_clase, query_clase.c.tweet_cuenta_id == CuentaTweet.id) \
        .filter(condition)
    return query.one_or_none()


def count_respuestas_mensiones(session, condition):
    query = session.query(func.count(Tweet.id)) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .filter(condition)
    return query.one_or_none()


def obtener_todas_clasificaciones(id_cuenta, mode, filtro):
    """
    Obtiene las clasificaciones
    :return:
    """
    # Conditions
    session = get_database_session()
    # Arma el query Clase
    modos, ids_clases, condition_cc = [], [], [CuentaClase.activo.is_(True)]
    # Condicion con Clases
    if filtro.get('minScore'):
        condition_cc.append(ClaseTweet.score >= filtro['minScore'])
    if filtro.get('maxScore'):
        condition_cc.append(ClaseTweet.score <= filtro['maxScore'])
    if filtro.get('clasesTweets', []):
        ids_clases = [c['id'] for c in filtro['clasesTweets']]
        condition_cc.append(ClaseTweet.cuenta_clase_id.in_(ids_clases))
    if filtro.get('seleccionados', []):
        modos = [c['valor'] for c in filtro['seleccionados']]
        if 'S' in modos:
            condition_cc.append(ClaseTweet.is_selected.is_(True))
    # Obtiene la condicion
    condition = obtener_filtros_tweet(filtro)
    # Arma el query Tweets
    query_clase = session.query(ClaseTweet.tweet_cuenta_id.label("id"),
                                func.count(ClaseTweet.id).label("clases")) \
        .join(CuentaTweet, CuentaTweet.id == ClaseTweet.tweet_cuenta_id) \
        .join(CuentaClase, CuentaClase.id == ClaseTweet.cuenta_clase_id) \
        .filter(CuentaTweet.cuenta_id == id_cuenta, *condition_cc) \
        .group_by(ClaseTweet.tweet_cuenta_id).subquery('query_clase')
    # Valida si tiene el filtro unidos
    if 'U' in modos:
        condition.append(query_clase.c.clases == len(ids_clases))
    # Arma Genera el Query
    query_tweet = session.query(Tweet.id.label("tweet"), ClaseTweet.cuenta_clase_id.label("id"), CuentaClase.nombre,
                                CuentaClase.color, func.date(Tweet.fecha).label("fecha"),
                                case((CuentaTweet.tipo == 'M', 1), else_=0).label("m"),
                                case((CuentaTweet.tipo == 'R', 1), else_=0).label("r"),
                                case((CuentaTweet.tipo == 'QT', 1), else_=0).label("qt"),
                                case((CuentaTweet.tipo == 'RT', 1), else_=0).label("rt")) \
        .join(CuentaClase, CuentaClase.id == ClaseTweet.cuenta_clase_id) \
        .join(CuentaTweet, CuentaTweet.id == ClaseTweet.tweet_cuenta_id) \
        .join(query_clase, query_clase.c.id == ClaseTweet.tweet_cuenta_id) \
        .join(Tweet, Tweet.id == CuentaTweet.tweet_id) \
        .filter(CuentaTweet.cuenta_id == id_cuenta,  *condition) \
        .subquery('query_tweet_c')
    # Obtiene el total por tipos
    total_tipos = obtener_total_tweets(session, query_tweet, True)
    if mode == 'TL':
        # Genera el Query Por Fecha
        query = session.query(query_tweet.c.id, query_tweet.c.nombre, query_tweet.c.color, query_tweet.c.fecha,
                              func.sum(query_tweet.c.m).label("M"),
                              func.sum(query_tweet.c.r).label("R"),
                              func.sum(query_tweet.c.qt).label("QT"),
                              func.sum(query_tweet.c.rt).label("RT"),
                              func.count(query_tweet.c.id).label("total"))\
            .group_by(query_tweet.c.id, query_tweet.c.nombre, query_tweet.c.color, query_tweet.c.fecha)
        items = objects_as_dict(query.all())
        # Obtien las fechas
        if items:
            clases = [item['nombre'] for item in items]
            labels = defaultdict(lambda: dict([(clase, {'total': 0}) for clase in clases]))
            labels['0'][clases[0]] = {'total': 0}
            for item in items:
                labels[item['fecha']][item['nombre']] = item
            items = labels
    else:
        # Genera el Query Por Clase
        query = session.query(query_tweet.c.id, query_tweet.c.color, query_tweet.c.nombre,
                              func.sum(query_tweet.c.m).label("M"),
                              func.sum(query_tweet.c.r).label("R"),
                              func.sum(query_tweet.c.qt).label("QT"),
                              func.sum(query_tweet.c.rt).label("RT"),
                              func.count(query_tweet.c.id).label("total")) \
            .group_by(query_tweet.c.id, query_tweet.c.nombre, query_tweet.c.color)
        items = objects_as_dict(query.all())
    return {'items': items, 'tipos': total_tipos}


def obtener_tweets_por_tipos(cuenta_id, filtro):
    """
    Obtiene los tweets por tipos
    :param cuenta_id:
    :param filtro:
    :return:
    """
    # Arama la condiicion
    condition = obtener_filtros_tweet(filtro)
    session = get_database_session()
    # Arma el query Tweets
    query = session.query(CuentaTweet.id, Tweet.autor_id, Tweet.fecha, Tweet.texto, CuentaTweet.tipo) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .join(ClaseTweet, CuentaTweet.id == ClaseTweet.tweet_cuenta_id) \
        .filter(CuentaTweet.cuenta_id == cuenta_id, *condition) \
        .group_by(CuentaTweet.id, Tweet.autor_id, Tweet.fecha, Tweet.texto, CuentaTweet.tipo) \
        .order_by(desc(Tweet.fecha)).limit(MAX_FILAS_POR_PAGINA)
    items = objects_as_dict(query.all())
    # Obtiene las autores
    tweets, autores = {}, defaultdict(lambda: [])
    for item in items:
        tweets[item['id']] = item
        autores[item['autor_id']].append(item['id'])
    obtener_autores_tweets(tweets, autores)
    return list(tweets.values())


def obtener_interacciones(id_cuenta, mode, fecha):
    """
    Obtiene las interaciones por fecha
    :param id_cuenta:
    :param fecha:
    :param mode:
    :return:
    """
    if mode == 'A':
        field_format = 'YYYY'
        condition_date = (1 == 1)
    elif mode == 'M':
        field_format = 'YYYY-MM'
        condition_date = func.to_char(Tweet.fecha, 'YYYY') == fecha.strftime("%Y")
    else:
        fecha_to = fecha - timedelta(days=30)
        field_format = 'YYYY-MM-DD'
        condition_date = and_(func.date(Tweet.fecha) >= fecha_to,
                              func.date(Tweet.fecha) <= fecha)

    field = func.to_char(Tweet.fecha, field_format).label("mode")
    condition = and_(CuentaTweet.cuenta_id == id_cuenta, condition_date)
    session = get_database_session()
    condition_m = and_(CuentaTweet.tipo == 'M', condition)
    mensiones = obtener_respuestas_mensiones(session, field, condition_m)
    condition_r = and_(CuentaTweet.tipo == 'R', condition)
    respuestas = obtener_respuestas_mensiones(session, field, condition_r)
    condition_qt = and_(CuentaTweet.tipo == 'QT', condition)
    citas = obtener_respuestas_mensiones(session, field, condition_qt)
    condition_rt = and_(CuentaTweet.tipo == 'RT', condition)
    retweets = obtener_respuestas_mensiones(session, field, condition_rt)

    labels = defaultdict(lambda: {'M': 0, 'R': 0, 'QT': 0, 'RT': 0})
    labels['0']['M'] = 0
    for value in mensiones:
        labels[value['mode']]['M'] = value['total']
    for value in respuestas:
        labels[value['mode']]['R'] = value['total']
    for value in citas:
        labels[value['mode']]['QT'] = value['total']
    for value in retweets:
        labels[value['mode']]['RT'] = value['total']
    session.close()

    # Retorna los labels
    return labels


def obtener_respuestas_mensiones(session, field, condition):
    """
    Obtiene las mensiones / respuestas / citas / retweets
    :param session:
    :param field:
    :param condition:
    :return:
    """
    query_tweet = session.query(Tweet.id, field) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .filter(condition).subquery('query_tweet')
    query = session.query(query_tweet.c.mode, func.count(query_tweet.c.id).label("total")) \
        .group_by(query_tweet.c.mode) \
        .order_by(query_tweet.c.mode)
    return objects_as_dict(query.all())


def obtener_interacciones_cuentas(id_cuenta, mode, fecha):
    """
    Obtiene las cuentas de interracion
    :param id_cuenta:
    :param mode:
    :param fecha:
    :return:
    """
    if mode == 'A':
        condition_date = func.to_char(Tweet.fecha, 'YYYY') == fecha
    elif mode == 'M':
        condition_date = func.to_char(Tweet.fecha, 'YYYY-MM') == fecha
    else:
        condition_date = func.to_char(Tweet.fecha, 'YYYY-MM-DD') == fecha
    condition = and_(CuentaTweet.cuenta_id == id_cuenta, condition_date)
    session = get_database_session()
    query_cuentas = session.query(Tweet.autor_id,
                          func.sum(case((CuentaTweet.tipo == 'M', 1), else_=0)).label("M"),
                          func.sum(case((CuentaTweet.tipo == 'R', 1), else_=0)).label("R"),
                          func.sum(case((CuentaTweet.tipo == 'QT', 1), else_=0)).label("QT"),
                          func.sum(case((CuentaTweet.tipo == 'RT', 1), else_=0)).label("RT"),
                          func.count(CuentaTweet.id).label("total")) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .filter(condition).group_by(Tweet.autor_id).subquery("query_cuentas")
    query = session.query(query_cuentas).order_by(desc(query_cuentas.c.total)).limit(MAX_FILAS_POR_PAGINA)
    items = objects_as_dict(query.all())
    # Arma el dicionario de cuentas
    autores = {}
    for item in items:
        autores[item['autor_id']] = item
    # Obtiene la info de los usuarios
    ids = ','.join(list(autores.keys()))
    result = gestor_usuario.buscar_cuenta_por_id(ids)
    for autor in result.get('data', []):
        autores[autor['id']]['usuario'] = gestor_usuario.obtener_user_data(autor)
    # Retorna los autores
    return list(autores.values())


def obtener_metrics_tweet(id_tweet):
    tw_api_rest = f"{url_tweets_metric}&ids={id_tweet}"
    with requests.get(tw_api_rest, auth=bearer_oauth) as resp:
        if resp.status_code == 200:
            return resp.json()
        else:
            log.error(f"Get Metrics (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No pudo obtener el usuario!")


def desactivar_tweet(id_tweet):
    """
    Desactiva el tweet
    :param id_tweet:
    :return:
    """
    session = get_database_session()
    tweet = session.query(Tweet).filter(Tweet.codigo == id_tweet).one_or_none()
    session.add(tweet)
    session.commit()


def guardar_tweet(data_tweet, cuentas):
    """
    Guarda el tweet
    :param data_tweet:
    :param cuentas:
    :return:
    """
    session = get_database_session()
    try:
        # Agrega los datos del tweet
        tweet = Tweet(
            codigo=data_tweet.get("codigo"),
            autor_id=data_tweet.get("autor_id"),
            texto=data_tweet.get("texto"),
            is_reply=data_tweet.get("is_reply"),
            fecha=data_tweet.get("fecha"),
        )
        # Agrega las entidades
        tweet.entidades = []
        for entidad in data_tweet.get("entidades"):
            tweet.entidades.append(EntidadTweet(
                tipo=entidad.get("tipo"),
                label=entidad.get("label"),
                valor=entidad.get("valor")
            ))
        # Agrega las cuentas
        tweet.cuentas = []
        for cuenta in cuentas:
            item = cuentas[cuenta]
            c_tweet = CuentaTweet(cuenta, item.get("tipo"), item.get("origen"), [])
            for clase in item.get("clasificaciones", []):
                c_tweet.clasificaciones.append(ClaseTweet(
                    cuenta_clase_id=clase.get("clase", {}).get('id'),
                    score=clase.get("score"),
                    is_selected=clase.get("is_selected"),
                ))
            tweet.cuentas.append(c_tweet)
        # Guarda los datos
        session.add(tweet)
        session.commit()
        # Obtiene los ids del Tweet
        for cuenta in tweet.cuentas:
            cuentas[cuenta.cuenta_id]['id'] = cuenta.id
    except Exception as error:
        log.error(f"ERROR: guardar_tweet -> {str(error)}")
        session.rollback()
    finally:
        session.close()


def obtener_data_tweet(id_cuenta, id_cuenta_tweet):
    """
    Obtiene los datos del tweet
    :param id_cuenta:
    :param id_cuenta_tweet:
    :return:
    """
    session = get_database_session()
    query = session.query(CuentaTweet) \
        .join(Tweet, CuentaTweet.tweet_id == Tweet.id) \
        .outerjoin(EntidadTweet, EntidadTweet.tweet_id == Tweet.id) \
        .outerjoin(ClaseTweet, ClaseTweet.tweet_cuenta_id == CuentaTweet.id) \
        .outerjoin(CuentaClase, ClaseTweet.cuenta_clase_id == CuentaClase.id) \
        .options(contains_eager("tweet")
                 .load_only(Tweet.codigo, Tweet.autor_id, Tweet.fecha, Tweet.texto),
                 contains_eager("tweet.entidades")
                 .load_only(EntidadTweet.tipo, EntidadTweet.label, EntidadTweet.valor)) \
        .options(contains_eager("clasificaciones")
                 .load_only(ClaseTweet.is_selected, ClaseTweet.score),
                 contains_eager("clasificaciones.clase")
                 .load_only(CuentaClase.nombre, CuentaClase.color)) \
        .options(load_only(CuentaTweet.activo, CuentaTweet.tipo, CuentaTweet.origen)) \
        .filter(CuentaTweet.id == id_cuenta_tweet, CuentaTweet.cuenta_id == id_cuenta, CuentaClase.activo.is_(True))\
        .order_by(desc(ClaseTweet.score))
    data_tweet = objects_as_dict(query.one_or_none())
    tweet = data_tweet.get('tweet', {})
    tweet.pop("id")
    data_tweet.update(tweet)
    data_tweet.pop("tweet")
    return data_tweet


def obtener_query_tweets(session, cuenta_id, filtro):
    """
    Arma el query princial de los tweets
    :param session:
    :param cuenta_id:
    :param filtro:
    :return:
    """
    modos, ids_clases, condition_cc = [], [], [CuentaClase.activo.is_(True)]
    # Condicion con Clases
    if filtro.get('minScore'):
        condition_cc.append(ClaseTweet.score >= filtro['minScore'])
        filtro.pop('minScore')
    if filtro.get('maxScore'):
        condition_cc.append(ClaseTweet.score <= filtro['maxScore'])
        filtro.pop('maxScore')
    if filtro.get('clasesTweets', []):
        ids_clases = [c['id'] for c in filtro['clasesTweets']]
        condition_cc.append(ClaseTweet.cuenta_clase_id.in_(ids_clases))
        filtro.pop('clasesTweets')
    if filtro.get('seleccionados', []):
        modos = [c['valor'] for c in filtro['seleccionados']]
        if 'S' in modos:
            condition_cc.append(ClaseTweet.is_selected.is_(True))
        filtro.pop('seleccionados')
    # Obtiene la condicion
    condition = obtener_filtros_tweet(filtro)
    # Arma el query Tweets
    query_clase = session.query(ClaseTweet.tweet_cuenta_id.label("id"),
                                func.count(ClaseTweet.id).label("clases")) \
        .join(CuentaTweet, CuentaTweet.id == ClaseTweet.tweet_cuenta_id) \
        .join(CuentaClase, CuentaClase.id == ClaseTweet.cuenta_clase_id) \
        .filter(CuentaTweet.cuenta_id == cuenta_id, *condition_cc) \
        .group_by(ClaseTweet.tweet_cuenta_id).subquery('query_clase')
    # Valida si tiene el filtro unidos
    if 'U' in modos:
        condition.append(query_clase.c.clases == len(ids_clases))
    # Arma el query tweets
    query_tweets = session.query(CuentaTweet.id, Tweet.codigo, Tweet.autor_id, Tweet.fecha, Tweet.texto,
                                 CuentaTweet.tipo, Tweet.activo) \
        .join(CuentaTweet, CuentaTweet.tweet_id == Tweet.id) \
        .join(query_clase, query_clase.c.id == CuentaTweet.id) \
        .filter(CuentaTweet.cuenta_id == cuenta_id, *condition) \
        .order_by(desc(Tweet.fecha))

    return query_tweets, condition_cc


def obtener_clasificacion_tweets(session, cuenta_id, condition_cc, tweets):
    """
    Obtiene las clasificaicones de los tweets
    :param session:
    :param cuenta_id:
    :param condition_cc:
    :param tweets:
    :return:
    """
    # Arma el query Clase
    condition_cc.append((CuentaTweet.id.in_(list(tweets.keys()))))
    query_clase = session.query(CuentaTweet.id, CuentaClase.nombre, CuentaClase.color, ClaseTweet.score,
                                ClaseTweet.is_selected) \
        .join(CuentaTweet, CuentaTweet.id == ClaseTweet.tweet_cuenta_id) \
        .join(CuentaClase, CuentaClase.id == ClaseTweet.cuenta_clase_id) \
        .filter(CuentaTweet.cuenta_id == cuenta_id, *condition_cc)
    clases = objects_as_dict(query_clase.all())
    for clase in clases:
        tweets[clase['id']]['clasificaciones'].append(clase)


def obtener_autores_tweets(tweets, autores):
    """
    Obtiene los autores de los tweets
    :param autores:
    :param tweets:
    :return:
    """
    autores_ids = list(autores.keys())
    # Agrega el usuario basio b
    for autor in autores_ids:
        for item_id in autores[autor]:
            tweets[item_id]['usuario'] = {}
    try:
        count, data, total = 0, [], len(autores_ids)
        modulo = total % 100
        if total > 100:
            for i in range(round((total - modulo) / 100)):
                count += 100  # Suma los 100 registros
                data += gestor_usuario.buscar_cuenta_por_id(
                    ','.join(autores_ids[(count - 100):count])
                ).get('data', [])
        if modulo != 0:
            data += gestor_usuario.buscar_cuenta_por_id(
                ','.join(autores_ids[count:total])
            ).get('data', [])
        for autor in data:
            for item_id in autores[autor['id']]:
                tweets[item_id]['usuario'] = gestor_usuario.obtener_user_data(autor)
    except Exception:
        # Agrega el usuario basio b
        pass


def obtener_total_tweets(session, query_tweet, es_grafica=False):
    """
    Obtiene el totoal de tweets
    :param session:
    :param query_tweet:
    :param es_grafica:
    :return:
    """
    if es_grafica:
        query_total = session.query(query_tweet.c.tweet,
                                    func.sum(query_tweet.c.m).label("m"),
                                    func.sum(query_tweet.c.r).label("r"),
                                    func.sum(query_tweet.c.qt).label("qt"),
                                    func.sum(query_tweet.c.rt).label("rt")) \
            .group_by(query_tweet.c.tweet).subquery("query_total")
        query_total = session.query(func.sum(case((query_total.c.m > 0, 1), else_=0)).label("M"),
                                    func.sum(case((query_total.c.r > 0, 1), else_=0)).label("R"),
                                    func.sum(case((query_total.c.qt > 0, 1), else_=0)).label("QT"),
                                    func.sum(case((query_total.c.rt > 0, 1), else_=0)).label("RT"))
    else:
        query_total = session.query(func.sum(case((query_tweet.c.tipo == 'M', 1), else_=0)).label("M"),
                                    func.sum(case((query_tweet.c.tipo == 'R', 1), else_=0)).label("R"),
                                    func.sum(case((query_tweet.c.tipo == 'QT', 1), else_=0)).label("QT"),
                                    func.sum(case((query_tweet.c.tipo == 'RT', 1), else_=0)).label("RT"))
    total_tipos = objects_as_dict(query_total.one_or_none())
    return obtener_totales_kas(total_tipos)


def obtener_tweets_pagina(cuenta_id, pagina, filtro):
    """
    Obtiener lista de tweets por pagina y filtro
    :param cuenta_id:
    :param filtro:
    :param pagina:
    :return:
    """
    session = get_database_session()
    # Condicion Tweets
    limite = (filtro.get('limite') or MAX_FILAS_POR_PAGINA)
    query, condition_cc = obtener_query_tweets(session, cuenta_id, filtro)
    # Genera un paginador
    paginator = Paginator(query, limite)
    items = objects_as_dict(paginator.page(pagina).object_list)
    # Obtiene las clases/autores
    tweets, autores = {}, defaultdict(lambda: [])
    for item in items:
        tweets[item['id']] = {**item, 'clasificaciones': []}
        autores[item['autor_id']].append(item['id'])
    obtener_clasificacion_tweets(session, cuenta_id, condition_cc, tweets)
    obtener_autores_tweets(tweets, autores)
    # Obtiene el total por tipo
    total_tipos = obtener_total_tweets(session, query.subquery('query_tweets'))
    session.close()
    return {'paginas': paginator.total_pages, 'tweets': list(tweets.values()), 'tipos': total_tipos}


def obtener_tweets_reporte(cuenta_id, filtro, con_clases, con_autores, con_totales):
    """
    Obtiener lista de tweets para reportes
    :param cuenta_id:
    :param filtro:
    :param con_clases:
    :param con_autores:
    :param con_totales:
    :return:
    """
    total_tipos = {}
    session = get_database_session()
    query, condition_cc = obtener_query_tweets(session, cuenta_id, filtro)
    items = objects_as_dict(query.all())
    query_tweets = query.subquery('query_tweets')
    # Obtiene las clases/autores
    tweets, autores = {}, defaultdict(lambda: [])
    for item in items:
        tweets[item['id']] = {**item, 'clasificaciones': [], 'tipo': get_nombre_tipo(item['tipo'])}
        autores[item['autor_id']].append(item['id'])
    if con_clases:  # Agrega las clasificaciones
        obtener_clasificacion_tweets(session, cuenta_id, condition_cc, tweets)
    if con_autores:  # Agrega los autores
        obtener_autores_tweets(tweets, autores)
    if con_totales:  # Agrega los totales
        total_tipos = obtener_total_tweets(session, query_tweets)
    # Obtiene la fecha max y min
    query_fecha = session.query(func.min(query_tweets.c.fecha), func.max(query_tweets.c.fecha))
    fechas_r = objects_as_dict(query_fecha.one_or_none())
    fechas = {'fecha_desde': '', 'fecha_hasta': ''}
    if filtro.get('fechaDesde'):
        fechas['fecha_desde'] = filtro['fechaDesde']
    else:
        if fechas_r[0]:
            fechas['fecha_desde'] = fechas_r[0].strftime("%Y-%m-%d")
    if filtro.get('fechaHasta'):
        fechas['fecha_hasta'] = filtro['fechaHasta']
    else:
        if fechas_r[1]:
            fechas['fecha_hasta'] = fechas_r[1].strftime("%Y-%m-%d")
    session.close()
    return {'tweets': list(tweets.values()), 'totales': total_tipos, **fechas}


def obtener_filtros_tweet(filtro):
    """
    Devuelve todas las condiciones segun el filtro
    :param filtro:
    :return:
    """
    # Arama la condicion
    condiition = [(1 == 1)]
    if filtro.get("criterio"):
        condiition.append(Tweet.texto.ilike(f"%{filtro['criterio']}%"))
    if filtro.get('ultimosDias', False):
        hasta = datetime.today()
        desde = hasta - timedelta(days=(filtro.get('dias') or 0))
        filtro['fechaDesde'] = desde.strftime(FORMAT_DATE)
        filtro['fechaHasta'] = hasta.strftime(FORMAT_DATE)
    if filtro.get('fechaDesde'):
        condiition.append(func.date(Tweet.fecha) >= filtro['fechaDesde'])
    if filtro.get('fechaHasta'):
        condiition.append(func.date(Tweet.fecha) <= filtro['fechaHasta'])
    if filtro.get('tiposTweets'):
        ids_tipos = [t['tipo'] for t in filtro['tiposTweets']]
        condiition.append(CuentaTweet.tipo.in_(ids_tipos))
    if filtro.get('autoresTweets'):
        ids_autores = [t['id'] for t in filtro['autoresTweets']]
        condiition.append(Tweet.autor_id.in_(ids_autores))
    if filtro.get('minScore'):
        condiition.append(ClaseTweet.score >= filtro['minScore'])
    if filtro.get('maxScore'):
        condiition.append(ClaseTweet.score <= filtro['maxScore'])
    if filtro.get('clasesTweets'):
        ids_clases = [c['id'] for c in filtro['clasesTweets'] if c['id']]
        condiition.append(ClaseTweet.cuenta_clase_id.in_(ids_clases))
    if filtro.get('seleccionados', []):
        modos = [c['valor'] for c in filtro['seleccionados']]
        if 'S' in modos:
            condiition.append(ClaseTweet.is_selected.is_(True))
    return condiition


def obtener_totales_kas(total_tipos):
    """
    Obtiene los totales por kas
    :param total_tipos:
    :return:
    """
    return {'M': human_format(total_tipos[0] or 0),
            'R': human_format(total_tipos[1] or 0),
            'QT': human_format(total_tipos[2] or 0),
            'RT': human_format(total_tipos[3] or 0)}
