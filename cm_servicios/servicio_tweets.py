"""
    C&M - Servicio Tweets
    =====================
    Api Rest Full -> Servicios de gestion de Tweets
    :autor @cmorocho
"""
from datetime import date
from flask import jsonify, request
from cm_gestores import gestor_tweets
from cm_gestores import gestor_usuario
from common_utils import human_format, cm_token_required_user, cm_token_required_cuenta


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_total_valores(id_cuenta):
    """
    API Rest obtiene los valores totales por cuenta
    :param id_cuenta:
    :return:
    """
    # Obtiene los valores totales por tipo
    resultado = gestor_tweets.obtener_total_valores(
        id_cuenta
    )  # Retorna los valores
    return jsonify({'data': resultado})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_interacciones(id_cuenta):
    """
    API Rest obtiene las interacciones por cuenta
    :param id_cuenta:
    :return:
    """
    # Obtiene las interacciones segun el modo
    resultado = gestor_tweets.obtener_interacciones(
        id_cuenta, request.args.get("modo"), date.today()
    )  # Retorna las interaccines
    return jsonify({'data': resultado})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_clasificaciones(id_cuenta):
    """
    API Rest obtiene las interacciones por cuenta
    :param id_cuenta:
    :return:
    """
    # Obtiene las clasficacines segun el modo
    resultado = gestor_tweets.obtener_todas_clasificaciones(
        id_cuenta, request.args.get("modo"), (request.json or {})
    )  # Retorna las clasficacines
    return jsonify({'data': resultado})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_tweets_filtro(id_cuenta, pagina):
    """
    API Rest obtiene los tweets por cuenta
    :param pagina:
    :param id_cuenta:
    :return:
    """
    # Obtiene los tweets por pagina segun el filtro
    resultado = gestor_tweets.obtener_tweets_pagina(
        id_cuenta, pagina, (request.json or {})
    )  # Retorna los tweets
    return jsonify({'data': resultado})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_data_tweet(id_cuenta, id_tweet):
    """
    API Rest Obtiene la data completa del Tweet
    :param id_cuenta:
    :param id_tweet:
    :return:
    """
    tweet = gestor_tweets.obtener_data_tweet(id_cuenta, id_tweet)
    # Obtiene la info del autor del tweet
    resultado = gestor_usuario.buscar_cuenta_por_id(tweet.get('autor_id'))
    if resultado.get("data"):
        usuario = resultado.get("data")[0]
        tweet['usuario'] = {
            'nombre': usuario.get("name"),
            'verified': usuario.get("verified"),
            'username': usuario.get('username'),
            'url_profile': usuario.get('profile_image_url'),
        }
    # Obtiene las metricas del tweet
    resultado = gestor_tweets.obtener_metrics_tweet(tweet.get('codigo'))
    if resultado.get("data"):
        metrics = resultado["data"][0]["public_metrics"]
        tweet['metricas'] = {
            'retweet': human_format(metrics.get("retweet_count")),
            'reply': human_format(metrics.get("reply_count")),
            'like': human_format(metrics.get("like_count")),
            'quote': human_format(metrics.get("quote_count")),
        }
    elif resultado.get("errors"):
        tweet['activo'] = False
    # Retorna la informacion del tweet
    return jsonify({'data': tweet})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_interacciones_cuentas(id_cuenta):
    """
    Api-Rest Obtiene las cuentas de interacion
    :param id_cuenta:
    :return:
    """
    # Obtiene las cuentas segun la fecha
    resultado = gestor_tweets.obtener_interacciones_cuentas(
        id_cuenta, request.args.get("modo"), request.args.get("fecha")
    )  # Retorna las cuentas
    return jsonify({'data': resultado})


@cm_token_required_user
@cm_token_required_cuenta
def api_obtener_tweets_por_tipos(id_cuenta):
    """
    Api-Rest Obtiene tweets por tipos
    :param id_cuenta:
    :return:
    """
    # Obtiene los tweets por el tipo
    resultado = gestor_tweets.obtener_tweets_por_tipos(
        id_cuenta, (request.json or {})
    )  # Retorna los tweets
    return jsonify({'data': resultado})
