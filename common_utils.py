"""
    C&M - Utils
    =====================
    Utilitario de la aplicacion
    :autor @cmorocho
"""
import jwt
import threading
import logging
from base64 import b64encode
from decimal import Decimal
from functools import wraps
from flask_sqlalchemy import Model
from datetime import datetime, date, time
from flask import current_app, request, jsonify
from werkzeug.wrappers import BaseResponse
from sqlalchemy.orm.base import instance_dict
from settings import BEARER_TOKEN, FORMAT_DATETIME, FORMAT_DATE, FORMAT_TIME, SECRET_KEY
log = logging.getLogger(__name__)


def synchronized(func):
    lock = threading.Lock()

    @wraps(func)
    def _wrap(*args, **kwargs):
        with lock:
            result = func(*args, **kwargs)
            return result

    return _wrap


def json_response(func):

    @wraps(func)
    def _wrap(*args, **kwargs):
        (data, code) = func(*args, **kwargs)
        return BaseResponse(data, status=code, content_type="application/json")

    return _wrap


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def bearer_oauth(res):
    """
    Method required by bearer token authentication.
    """
    res.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    res.headers["User-Agent"] = "v2FilteredStreamPython"
    return res


def get_value_fomato(valor):
    if isinstance(valor, datetime):
        return valor.strftime(FORMAT_DATETIME)
    elif isinstance(valor, date):
        return valor.strftime(FORMAT_DATE)
    elif isinstance(valor, time):
        return valor.strftime(FORMAT_TIME)
    if isinstance(valor, bytes):
        return b64encode(valor).decode()
    elif isinstance(valor, Decimal):
        return float(valor)
    else:
        return valor


def objects_as_dict(obj):
    """
    Metodo para pasar los datos del resultado de una consulta sqlAlchemy a diccinario
    :param obj:
    :return:
    """
    # validar si es una lista
    if isinstance(obj, list):
        lista_new = []
        for o in obj:
            dict_new = {}
            # tomo todas las columnas de la tabla
            if isinstance(o, Model):
                dict_datos = instance_dict(o)
                if dict_datos.get('_sa_instance_state'):
                    del dict_datos['_sa_instance_state']
            else:
                dict_datos = dict(zip(o._fields, o))
            for colum in dict_datos:
                valor = objects_as_dict(dict_datos.get(colum))
                dict_new[colum] = get_value_fomato(valor)
            lista_new.append(dict_new)
        return lista_new
    elif isinstance(obj, Model):
        dict_new = {}
        # tomo todas las columnas de la tabla
        if isinstance(obj, Model):
            dict_datos = instance_dict(obj)
            if dict_datos.get('_sa_instance_state'):
                del dict_datos['_sa_instance_state']
        else:
            dict_datos = dict(zip(obj._fields, obj))
        for colum in dict_datos:
            valor = objects_as_dict(dict_datos.get(colum))
            dict_new[colum] = get_value_fomato(valor)
        return dict_new
    else:
        return obj


def get_database_session():
    return current_app.current_session()


def get_chat_bot_app():
    return current_app.cm_chat_bot


def get_logger_app():
    return current_app.logger


def round_numero(numero, tipo=0):
    if tipo == 1:
        num_rond = round(numero)
        return num_rond + 1 if num_rond < numero else num_rond
    elif tipo == -1:
        num_rond = round(numero)
        return num_rond - 1 if num_rond > numero else num_rond
    else:
        return round(numero)


def get_nombre_tipo(tipo):
    if tipo == 'M':
        return "Mencion"
    elif tipo == 'R':
        return "Respuesta"
    elif tipo == 'QT':
        return "Cita Tweet"
    else:
        return "Retweet"


def cm_token_validate():
    """
    Metodod que valida el token
    :return:
    """
    token = None  # Verifica si tiene el token
    if 'CM-Token' in request.headers:
        token = request.headers['CM-Token']
    if not token:
        raise Exception('CM Token es requerido para esta accion')
    # Obtiene el usuario
    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    with current_app.app_context():
        return current_app.cm_api_app.obtener_usuario_por_id(
            data['usuario']
        )  # Retorna el usuario


def cm_token_required_user(f):

    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            # Valida que tenga CM Token
            usuario = cm_token_validate()
            if usuario:  # Valida el usuario
                try:  # Ejecuta el servicio
                    return f(usuario.id, *args, **kwargs)
                except Exception as error:
                    log.error(f"ERROR: CM | {f.__name__} -> {str(error)}")
                    return jsonify({'error': str(error)}), 500
            # Retorna Usuario no autorizado
            return jsonify({'error': 'Este usuario no esta autorizado'}), 401
        except Exception as error:
            log.error(f"ERROR: CM Token -> {str(error)}")
            return jsonify({'error': str(error)}), 401

    return decorator


def cm_token_required_admin(f):

    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            # Valida que tenga CM Token
            usuario = cm_token_validate()
            # Valida que el usuario sea admin
            if usuario and usuario.es_admin:
                try:  # Ejecuta el servicio
                    return f(usuario.id, *args, **kwargs)
                except Exception as error:
                    log.error(f"ERROR: CM | {f.__name__} -> {str(error)}")
                    return jsonify({'error': str(error)}), 500
            # Retorna Usuario no autorizado
            return jsonify({'error': 'Este usuario no esta autorizado'}), 403
        except Exception as error:
            log.error(f"ERROR: CM Token -> {str(error)}")
            return jsonify({'error': str(error)}), 401

    return decorator


def cm_token_required_cuenta(f):
    """
    Metodo cuenta asociada requerida
    :param f:
    :return:
    """
    @wraps(f)
    def decorator(*args, **kwargs):
        # Valida que el usuario y la cuenta
        with current_app.app_context():
            # Obtiene la cuenta asociada
            cuenta = current_app.cm_api_app.verificar_cuenta_usuario(
                args[0], kwargs.get('id_cuenta')
            )  # Verifica la cuenta
        if cuenta:  # Ejecuta el servicio
            return f(**kwargs)
        else:
            # Retorna Usuario no autorizado
            return jsonify({'error': 'El usuario no esta autorizado'}), 403

    return decorator
