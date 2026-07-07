"""
    C&M - Servicio Usuarios
    =====================
    Api Rest Full ->  Servicios para la gestion de usuarios
    :autor @cmorocho
"""
from flask import jsonify, request
from cm_gestores import gestor_usuario
from common_utils import get_chat_bot_app, cm_token_required_user, cm_token_required_admin


def api_autenticar_usuario():
    """
    API Rest autentifica el usuario
    :return:
    """
    try:
        usuario = request.json  # Obtiene la info del usuario
        if usuario.get("correo") and usuario.get('password'):
            session = gestor_usuario.autenticar_usuario(usuario)
            if session:
                # Obtiene la info de la cuenta
                resultado = gestor_usuario.buscar_cuenta_por_id(session['cuenta']['id'], True)
                if resultado.get("data"):
                    cuenta = resultado.get("data")[0]
                    cuenta['public_metrics'] = gestor_usuario.obtener_metricas_kas(cuenta['public_metrics'])
                    cuenta['profile_image_url'] = cuenta['profile_image_url'].replace("_normal.", "_400x400.")
                    session['cuenta'].update(cuenta)
                # Retorna la session del usuario
                return jsonify({'session': session})
            else:
                return jsonify({'error': "El correo o la contraseña es incorrecto!"}), 500
        else:
            return jsonify({'error': "La informacion del usuario es requerida!"}), 500
    except Exception as error:
        return jsonify({'error': str(error)}), 500


def api_buscar_cuenta_por_id(id_cuenta):
    """
    API Rest Busca cuenta de twitter por el id
    :param id_cuenta:
    :return:
    """
    cuenta = None  # Obtiene la info de la cuenta
    result = gestor_usuario.buscar_cuenta_por_id(id_cuenta, True)
    if result.get("data"):
        cuenta = result.get("data")[0]
        cuenta['public_metrics'] = gestor_usuario.obtener_metricas_kas(cuenta['public_metrics'])
        cuenta['profile_image_url'] = cuenta['profile_image_url'].replace("_normal.", "_400x400.")
    # Retorna la info de la cuenta
    return jsonify({'data': cuenta})


def api_buscar_cuenta_por_nombre(username):
    """
    API Rest Busca usuarios de twitter por el username
    :param username:
    :return:
    """
    cuenta = None
    result = gestor_usuario.buscar_usuario_por_nombre(username)
    if result.get("data"):
        cuenta = result["data"][0]
        # Convierte los numeros a KAS
        cuenta['profile_image_url'] = cuenta['profile_image_url'].replace("_normal.", "_400x400.")
        # Convierte los numeros a KAS
        cuenta['public_metrics'] = gestor_usuario.obtener_metricas_kas(cuenta['public_metrics'])
        if request.args.get("modo") == 'E':
            cuenta = gestor_usuario.obtener_user_data(cuenta)
    return jsonify({'data': cuenta})


@cm_token_required_user
def api_enviar_mensaje(id_usuario, id_cuenta):
    """
    Api-Rest que envia el mensaje a ibm watson
    :return:
    """
    chat_boot = get_chat_bot_app()
    try:
        # Obtiene los datos
        data = (request.json or {})
        if data.get("mensaje") and data.get("chat_session"):
            # Obtiene el mensaje del cleinte y lo envia a watson
            mensajes = chat_boot.enviar_mensaje(data['chat_session'], data['mensaje'])
        else:
            mensajes = chat_boot.iniciar_chat_boot(data['chat_session'])
        return jsonify({'mensajes': mensajes})
    except Exception as e:
        try:
            chat_session = chat_boot.obtener_session()
            mensajes = chat_boot.iniciar_chat_boot(chat_session)
            return jsonify({'mensajes': mensajes, 'chat_session': chat_session})
        except Exception as e:
            return jsonify({'error': str(e)})


@cm_token_required_user
def api_obtener_cuentas_usuario(id_usuario, modo):
    """
    API Rest obtiene las cuentas del usuario
    :param id_usuario:
    :param modo:
    :return:
    """
    if modo == 'WI':
        cuentas = {}  # Obtiene las cuentas
        items = gestor_usuario.obtener_cuentas_usuario(
            id_usuario, request.args.get("cuenta_id")
        )  # Agrega la info de las cuentas
        for item in items:
            cuentas[item['cuenta_id']] = item
        # Obtiene la info de las cuentas
        ids = ','.join(list(cuentas.keys()))
        resultado = gestor_usuario.buscar_cuenta_por_id(ids)
        for autor in resultado.get('data', []):
            cuentas[autor['id']]['usuario'] = gestor_usuario.obtener_user_data(autor)
        # Obtiene los valores
        cuentas = list(cuentas.values())
    else:  # No agrega la info de las cuentas
        cuentas = gestor_usuario.obtener_cuentas_usuario(
            id_usuario, request.args.get("cuenta_id")
        )  # Retorna las cuentas
    return jsonify({'data': cuentas})


@cm_token_required_admin
def api_obtener_usuarios_cuentas(id_usuario):
    """
    API Rest obtiene todos los usuarios
    :param id_usuario:
    :return:
    """
    # Obtiene la lista de usuarios
    resultado = gestor_usuario.obtener_usuarios_cuentas(
        id_usuario
    )  # Retorna los usuarios
    return jsonify({'data': resultado})


@cm_token_required_admin
def api_agregar_usuario_cuenta(id_usuario):
    """
    API Rest obtiene todos los usuarios
    :param id_usuario:
    :return:
    """
    # Agrega un usuario
    resultado = gestor_usuario.agregar_usuario_cuenta(
        id_usuario, (request.json or {})
    )  # Retorna el usuario creado
    return jsonify({'data': resultado})


@cm_token_required_admin
def api_eliminar_usuario_cuenta(id_usuario, usuario_id):
    """
    API Rest elimina el usuario
    :param id_usuario:
    :param usuario_id:
    :return:
    """
    gestor_usuario.eliminar_usuario_cuenta(
        id_usuario, usuario_id
    )  # Elimina el usuario
    return jsonify({'data': "Usuario eliminado con exito!"})


@cm_token_required_admin
def api_agregar_cuenta_usuario(id_usuario):
    """
    API Rest agrega una cuenta de twitter al usuario
    :param id_usuario:
    :return:
    """
    # Agrega la cuenta al usuario
    resultado = gestor_usuario.agregar_cuenta_usuario(
        id_usuario, (request.json or {})
    )  # Retorna el id de la cuenta agregada
    return jsonify({'data': resultado})


@cm_token_required_user
def api_obtener_clases_cuenta(id_usuario, id_cuenta):
    """
    API Rest Busca las clases de una cuenta
    :param id_usuario:
    :param id_cuenta:
    :return:
    """
    # Obtiene las clases de la cuenta
    resultado = gestor_usuario.obtener_clases_cuentas(
        id_usuario, [id_cuenta], request.args.get("activo")
    )  # Retorna las clases
    return jsonify({'data': list(resultado.values())[0]})


@cm_token_required_admin
def api_agregar_clase_cuenta(id_usuario, id_cuenta):
    """
    API Rest agregar una clase a la cuenta
    :param id_usuario:
    :param id_cuenta:
    :return:
    """
    # Vincula la clase a la cuenta
    clase_id = gestor_usuario.agregar_clase_cuenta(
        id_usuario, id_cuenta, request.json
    )  # Retorna el id de la clase creada
    return jsonify({'data': clase_id})


@cm_token_required_admin
def api_eliminar_clase_cuenta(id_usuario, id_clase):
    """
    API Rest elimina clases a las cuentas
    :param id_usuario:
    :param id_clase:
    :return:
    """
    # Elimina la clase
    gestor_usuario.eliminar_clase_cuenta(id_clase)
    return jsonify({'data': "Clase eliminada con exito!"})


@cm_token_required_user
def api_obtener_acciones_cuenta(id_usuario, id_cuenta):
    """
    API Rest Obtiene las acciones de una cuenta
    :param id_usuario:
    :param id_cuenta:
    :return:
    """
    # Obtiene las acciones de la cuenta
    resultado = gestor_usuario.obtener_acciones_cuentas(
        id_cuenta, request.args.get("favoritos")
    )  # Retorna las acciones
    return jsonify({'data': resultado})


@cm_token_required_admin
def api_agregar_accion_cuenta(id_usuario, id_cuenta):
    """
    API Rest agregar accion a las cuentas
    :param id_usuario:
    :param id_cuenta:
    :return:
    """
    # Agrega la accion a la cuenta
    resultado = gestor_usuario.agregar_accion_cuenta(
        id_usuario, id_cuenta, request.json
    )  # Retorna el id de la accion creada
    return jsonify({'data': resultado})


@cm_token_required_admin
def api_eliminar_accion_cuenta(id_usuario, id_accion):
    """
    API Rest elimina la accion de la cuenta
    :param id_usuario:
    :param id_accion:
    :return:
    """
    # Elimina la accion de la cuenta
    gestor_usuario.eliminar_accion_cuenta(id_accion)
    return jsonify({'data': "Accion eliminada con exito!"})


@cm_token_required_admin
def api_favorito_accion_cuenta(id_usuario, id_accion):
    """
    API Rest elimina accion a las cuentas
    :param id_usuario:
    :param id_accion:
    :return:
    """
    # Agrega la accion a favoritos
    gestor_usuario.favorito_accion_cuenta(id_accion)
    return jsonify({'data': "Accion agregada a favorito con exito!"})
