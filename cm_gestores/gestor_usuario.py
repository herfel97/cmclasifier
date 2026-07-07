"""
    C&M - Gestor Usuarios
    =====================
    Logica para la gestion de usuarios
    :autor @cmorocho
"""
import jwt
import requests
import logging
import datetime
from sqlalchemy import desc
from pydantic.utils import defaultdict
from sqlalchemy.orm import load_only, contains_eager
from werkzeug.security import generate_password_hash, check_password_hash
from cm_modelos.modelo_tweets import ClaseTweet, CuentaTweet
from cm_modelos.modelo_usuario import UsuarioCuenta, CuentaClase, CuentaAccion, Usuario
from common_utils import objects_as_dict, bearer_oauth, synchronized, get_database_session, human_format
# URLs api twitter
from settings import URL_API_TWITTER, SECRET_KEY

log = logging.getLogger(__name__)

# URLs Api Tweter
url_user_by_id = f"{URL_API_TWITTER}/users/?ids=ID_C&user.fields=name,username,profile_image_url,verified"
url_user_by_name = f"{URL_API_TWITTER}/users/by?user.fields=description,profile_image_url,verified,public_metrics"
url_stream_rules = f"{URL_API_TWITTER}/tweets/search/stream/rules"
quote_url = "https://twitter.com/{}/status/"


def autenticar_usuario(data):
    """
    Autentica al usuario y devuelve el CM Token
    :param data:
    :return:
    """
    usuario = obtener_usuario_por_correo(data.get("correo"))
    if usuario and check_password_hash(usuario.password, data.get('password')):
        # Genera el CM Token
        exp_in = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        token = jwt.encode({'usuario': usuario.id, 'exp': exp_in}, SECRET_KEY, "HS256")
        # Obtiene la cuenta por defecto
        cuenta = UsuarioCuenta.query.filter_by(usuario_id=usuario.id).first()
        return {  # Retorna la session
            'token': token,
            'cuenta': {'id': cuenta.cuenta_id, "username": cuenta.username},
            'usuario': {'id': usuario.id, 'nombre': usuario.nombre,
                        'correo': usuario.correo, 'es_admin': usuario.es_admin},
        }


def agregar_usuario_cuenta(id_usuario, data, es_admin=False):
    """
    Crea al usuario
    :param id_usuario:
    :param data:
    :param es_admin:
    :return:
    """
    # Valida que haya datos
    if not (data.get("nombre") and data.get("correo")
            and data.get('password') and data.get("cuentas")):
        raise Exception("La informacion del usuario es requerida!")
    # Valida que no exista el correo
    existe = obtener_usuario_por_correo(data['correo'], False)
    if existe:
        raise Exception("El correo ya se encuentra registrado!")
    # Obtiene la session
    session = get_database_session()
    # Encripta la contraseña y guarda el usuario
    password = generate_password_hash(data.get('password'), method='sha256')
    usuario = Usuario(
        nombre=data.get("nombre"),
        correo=data.get("correo"),
        activo=data.get("activo"),
        es_admin=es_admin,
        password=password,
        usuario_registro=id_usuario
    ).save(session)
    # Agrega la cuenta por defecto
    agregar_cuenta_usuario(usuario.id, data['cuentas'][0], session)
    # Retrona el usuario
    return usuario.id


def obtener_usuario_por_correo(correo, activo=True):
    """
    Obtiene el usuario del sistema por el correo
    :return:
    """
    filtros = [Usuario.correo.like(correo)]
    if activo:
        filtros.append(Usuario.activo.is_(activo))
    # Retorna el usuario
    return Usuario.query.filter(*filtros).first()


def obtener_usuario_por_id(id_usuario):
    """
    Obtiene el usuario del sistema por el id
    :return:
    """
    return Usuario.query.filter(Usuario.id == id_usuario).first()


# CONSUME APIS REST TWITTER
def buscar_usuario_por_nombre(username):
    """
    Consume Twitter Api Rest y obtiene el username
    :param username:
    :return:
    """
    ur_api_rest = f"{url_user_by_name}&usernames={username}"
    with requests.get(ur_api_rest, auth=bearer_oauth) as resp:
        if resp.status_code == 200:
            return resp.json()
        else:
            log.error(f"Get rules (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No pudo obtener el usuario!")


def buscar_cuenta_por_id(id_user, public_metric=False):
    """
    Consume Twitter Api Rest y obtiene el usuario
    :param id_user:
    :param public_metric:
    :return:
    """
    if not id_user:
        return {}
    url_api_rest = url_user_by_id.replace("ID_C", id_user)
    if public_metric:
        url_api_rest += ',public_metrics'
    with requests.get(url_api_rest, auth=bearer_oauth) as resp:
        if resp.status_code == 200:
            return resp.json()
        else:
            log.error(f"Get rules (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No pudo obtener el usuario!")


def obtener_reglas_cuenta():
    """
    Consume Twitter Api Rest y obtiene las reglas de Stream
    :return:
    """
    with requests.get(url_stream_rules, auth=bearer_oauth) as resp:
        if resp.status_code == 200:
            return resp.json()
        else:
            log.error(f"Get rules (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No pudo obtener las reglas!")


def elimina_regla_cuenta(reglas):
    """
    Consume Twitter Api Rest y Elimina la reglas del Stream
    :param reglas:
    :return:
    """
    payload = {"delete": {"ids": [r["id"] for r in reglas]}}
    with requests.post(url_stream_rules, auth=bearer_oauth, json=payload) as resp:
        if resp.status_code != 200:
            log.error(f"Del rules (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No pudo eliminar las reglas!")


def agrega_regla_cuenta(id_cuenta, cuenta):
    """
    Consume Twitter Api Rest y Agrega las reglas del Stream
    :param id_cuenta:
    :param cuenta:
    :return:
    """
    payload = {"add": [
        {"value": f'(({cuenta} -is:retweet) OR (retweets_of:{cuenta[1:]}) OR '
                  f'(url:"{quote_url.format(cuenta[1:])}" is:quote)) -from:{id_cuenta}', "tag": id_cuenta}]
    }
    reglas = obtener_reglas_cuenta()
    if reglas.get("data"):
        reglas = list(filter(lambda r: r.get('tag') == id_cuenta, reglas['data']))
        if reglas:
            elimina_regla_cuenta(reglas)
    # Agrega la regla de la cuenta
    with requests.post(url_stream_rules, auth=bearer_oauth, json=payload) as resp:
        if resp.status_code != 201:
            log.error(f"Add rules (HTTP {resp.status_code}): {resp.text}")
            raise Exception(f"[ {resp.status_code} ] | No se pudo agregar las reglas!")


def obtener_cuentas_usuario(id_usuario, cuenta_id=None):
    """
    Obtiene todas la cuentas del usuario
    :return:
    """
    condition = [(UsuarioCuenta.usuario_id == id_usuario)]
    if cuenta_id:
        condition.append(UsuarioCuenta.cuenta_id != cuenta_id)
    return objects_as_dict(
        UsuarioCuenta.query.filter(*condition).options(
            load_only("cuenta_id", "username")).all()
    )


@synchronized
def agregar_cuenta_usuario(id_usuario, cuenta, session=None):
    """
    Agrega una cuenta al usuario
    :param id_usuario:
    :param cuenta:
    :param session:
    :return:
    """
    # Valida que tenga los campos
    if not (cuenta.get('cuenta_id') or cuenta.get('username')):
        raise Exception("La informacion de la cuenta es requerida")
    # Valida que sea unsuairo
    if not cuenta['username'].startswith("@"):
        raise Exception("El username de la cuenta es incorrecta!")
    # Obtiene la session
    if not session:
        session = get_database_session()
    # Valida que no exista la cuenta agregado
    c_cuenta = obtener_usuario_cuentas(id_usuario, [cuenta['cuenta_id']])
    if c_cuenta:  # Valida la cuenta
        if c_cuenta[0].username == cuenta['username']:
            raise Exception("Esta cuenta ya se encuentra agregada!")
        else:
            raise Exception(f"Esta cuenta ya se encuentra agregada con otro nombre! "
                            f"{c_cuenta[0].username} | {cuenta['username']}")
    else:
        # Agrega la cuenta al usuario
        cuenta_u = UsuarioCuenta(usuario_id=id_usuario,
                                 cuenta_id=cuenta['cuenta_id'],
                                 username=cuenta['username']).save(session)
        # Crea la clase default
        default_name = "sin clasificacion",
        default_descrip = "Clase para identificar los tweets que no tienen clasificacion"
        clase = CuentaClase.query.filter_by(cuenta_id=cuenta['cuenta_id'], default=True,
                                            nombre=default_name).first()
        if not clase:  # Valida si tiene la clase por defecto
            clase = CuentaClase(cuenta_id=cuenta['cuenta_id'], nombre=default_name, default=True,
                                descripcion=default_descrip, min_score=0.0, max_score=100).save(session)
        # Actualiza las clases por defecto
        agregar_clase_default(session, cuenta['cuenta_id'], clase.id)
        # Actualiza reglas del stream
        cuentas = UsuarioCuenta.query.filter_by(username=cuenta['username']).all()
        if len(cuentas) == 1:
            agrega_regla_cuenta(cuenta['cuenta_id'], cuenta['username'])
        # Retorna el id del registro guardado
        return cuenta_u.id


def agregar_clase_default(session, id_cuenta, clase_id):
    """
    Setea una clase por defecto a los tweets sin clasificacion
    :return:
    """
    # Alactualiza la clasificaicon de tweets
    query = session.query(CuentaTweet) \
        .outerjoin(ClaseTweet, ClaseTweet.tweet_cuenta_id == CuentaTweet.id) \
        .options(contains_eager("clasificaciones")) \
        .filter(CuentaTweet.cuenta_id == id_cuenta, ClaseTweet.id.is_(None))
    items = query.all()
    for item in items:
        item.clasificaciones = [ClaseTweet(clase_id, 100, True)]
    session.add_all(items)
    session.commit()


def obtener_clases_cuentas(id_usuario, ids_cuentas, activo):
    """
    Obtiene todas la clases de la cuentas
    :param id_usuario:
    :param ids_cuentas:
    :param activo:
    :return:
    """
    cuentas_u = obtener_usuario_cuentas(id_usuario, ids_cuentas)
    if id_usuario and cuentas_u:
        ids_cuentas = [cu.cuenta_id for cu in cuentas_u]
    # Agrega la condicion de la cuenta
    condition = [CuentaClase.cuenta_id.in_(ids_cuentas)]
    colums = ["cuenta_id", "nombre", "min_score", "max_score", "default", "color"]
    if activo == '1':
        condition.append(CuentaClase.activo == True)
    else:
        colums += ["activo", "descripcion"]
    # Arma el query
    query = CuentaClase.query.filter(*condition).options(load_only(*colums))\
        .order_by(CuentaClase.default, CuentaClase.min_score)
    clases = objects_as_dict(query.all())
    cuentas = defaultdict(lambda: [])
    for clase in clases:
        cuentas[clase['cuenta_id']].append(clase)
    return cuentas


def obtener_usuario_cuentas(id_usuario, cuenta_ids):
    """
    Obtiene el usuario y la cuenta
    :param id_usuario:
    :param cuenta_ids:
    :return:
    """
    return UsuarioCuenta.query.filter(UsuarioCuenta.usuario_id == id_usuario,
                                      UsuarioCuenta.cuenta_id.in_(cuenta_ids)).all()


def obtener_usuarios_cuentas(id_usuario):
    """
    Obtiene todos los usuarios registrados
    :param id_usuario:
    :return:
    """
    session = get_database_session()
    query = session.query(Usuario)\
        .join(UsuarioCuenta, UsuarioCuenta.usuario_id == Usuario.id) \
        .options(contains_eager("cuentas").load_only(UsuarioCuenta.cuenta_id, UsuarioCuenta.username)) \
        .options(load_only(Usuario.nombre, Usuario.correo, Usuario.activo))\
        .filter(Usuario.id != id_usuario)
    # Retorna los usuarios
    return objects_as_dict(query.all())


def eliminar_usuario_cuenta(id_usuario, usuario_id):
    """
    Elimina el usuario de la plataforma
    :param id_usuario:
    :param usuario_id:
    :return:
    """
    usuario = Usuario.query.filter(Usuario.id == usuario_id,  Usuario.id != id_usuario,
                                   Usuario.usuario_registro == id_usuario).first()
    if usuario:  # Elimina el usuario
        usuario.delete()
    else:
        raise Exception("El usuario no puede ser eliminado!")


def agregar_clase_cuenta(id_usuario, id_cuenta, clase):
    """
    Agrega/Actualiza la clase de una cuenta
    :param id_usuario:
    :param id_cuenta:
    :param clase:
    :return:
    """
    nombre = clase.get('nombre', "").strip().lower()
    # Valida que no exista la clase agregado
    c_clase = CuentaClase.query.filter(CuentaClase.cuenta_id == id_cuenta,
                                       CuentaClase.nombre.like(nombre)).first()
    if clase.get("id") and c_clase and clase['id'] == c_clase.id:
        c_clase = None
    if c_clase:
        raise Exception("Esta clase ya se encuentra agregada!")
    else:
        # Guarda la Clase Cuenta
        session = get_database_session()
        cuenta_c = CuentaClase(id=clase.get("id"),
                               nombre=nombre,
                               cuenta_id=id_cuenta,
                               color=clase.get("color"),
                               usuario_registro=id_usuario,
                               activo=clase.get("activo", True),
                               min_score=clase.get("min_score"),
                               max_score=clase.get("max_score"),
                               descripcion=clase.get("descripcion")).save(session)
        # Retorna el id generado
        return cuenta_c.id


def eliminar_clase_cuenta(id_clase):
    """
    Elimina la clase de la cuenta
    :param id_clase:
    :return:
    """
    session = get_database_session()
    # Obtiene el total de Tweets
    ids_clase = count_clasificaciones_label(session, id_clase)
    if ids_clase:
        session.query(ClaseTweet) \
            .filter(ClaseTweet.id.in_([l[0] for l in ids_clase])).delete()
    # Elimina la clase
    CuentaClase(id=id_clase).delete(session)


def obtener_acciones_cuentas(id_cuenta, favorito):
    """
    Obtiene todas la acciones de la cuentas
    :param id_cuenta:
    :param favorito:
    :return:
    """
    condicion = [CuentaAccion.cuenta_id == id_cuenta]
    if favorito == 'true':
        condicion.append(CuentaAccion.favorito.is_(True))
    # Arma el query
    query = CuentaAccion.query.filter(*condicion).order_by(desc(CuentaAccion.favorito))
    return objects_as_dict(query.all())


def agregar_accion_cuenta(id_usuario, id_cuenta, accion):
    """
    Agrega/Actualiza la clase de una cuenta
    :param id_usuario:
    :param id_cuenta:
    :param accion:
    :return:
    """
    session = get_database_session()
    codigo = accion.get('codigo', "").strip()
    # Valida que no exista la accion agregado
    c_accion = CuentaAccion.query.filter(CuentaAccion.cuenta_id == id_cuenta,
                                         CuentaAccion.codigo.ilike(codigo)).first()
    if accion.get("id") and accion['id'] == c_accion.id:
        c_accion = None
    if c_accion:
        raise Exception("Esta accion ya se encuentra agregada!")
    else:
        # Guarda la Clase Cuenta
        c_cuenta = CuentaAccion(
            id=accion.get("id"),
            codigo=codigo,
            cuenta_id=id_cuenta,
            usuario_registro=id_usuario,
            nombre=accion.get("nombre"),
            descripcion=accion.get("descripcion"),
            activo=accion.get("activo", True),
            json_filtros=accion.get("json_filtros"),
            json_reporte=accion.get("json_reporte")).save(session)
        # Retorna el id generado
        return c_cuenta.id


def eliminar_accion_cuenta(id_accion):
    """
    Elimina la accion de la cuenta
    :param id_accion:
    :return:
    """
    # Obtiene la accion del usuario
    accion = CuentaAccion.query.filter(CuentaAccion.id == id_accion).first()
    if accion:  # Valida la accion
        accion.delete()
    else:
        raise Exception("La accion no puede ser eliminada!")


def favorito_accion_cuenta(id_accion):
    """
    Agrega a favorito la accion de la cuenta
    :param id_usuario:
    :param id_accion:
    :return:
    """
    accion = CuentaAccion.query.filter(CuentaAccion.id == id_accion).first()
    if accion:
        accion.favorito = not accion.favorito
        accion.save()
    else:
        raise Exception("La accion expecificada no existe!")


def count_clasificaciones_label(session, id_clase):
    query = session.query(ClaseTweet.id) \
        .filter(ClaseTweet.cuenta_clase_id == id_clase)
    return query.all()


def obtener_metricas_kas(metrics):
    """
    Obtiene las metricas de una cuenta
    :param metrics:
    :return:
    """
    return {
        'followers': human_format(metrics.get("followers_count")),
        'following': human_format(metrics.get("following_count")),
        'tweets': human_format(metrics.get("tweet_count")),
    }


def obtener_user_data(autor, add_arroba=False):
    """
    Retorna los datos de la cuenta
    :param autor:
    :param add_arroba:
    :return:
    """
    arroba = "@" if add_arroba else ""
    return {
        'id': autor['id'],
        'nombre': autor['name'],
        'username': f"{arroba}{autor['username']}",
        'verified': autor['verified'],
        'url_profile': autor['profile_image_url']
    }
