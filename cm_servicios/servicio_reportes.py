"""
    C&M - Servicio Reportes
    =====================
    Api Rest Full ->  Servicios para la gestion de reportes
    :autor @cmorocho
"""

from datetime import datetime
from flask import jsonify, request
from cm_gestores import gestor_usuario
from cm_gestores import gestor_reportes
from flask import send_file

from common_utils import cm_token_required_user, cm_token_required_cuenta


@cm_token_required_user
@cm_token_required_cuenta
def generar_por_accion(id_cuenta):
    """
    Genera el reporte segun la accion
    :return:
    """
    try:
        accion = (request.json or {})
        # Obtiene la info de la cuenta
        cuenta = {}
        result = gestor_usuario.buscar_cuenta_por_id(f"{id_cuenta}", True)
        if result.get('data'):
            user = result['data'][0]
            cuenta = gestor_usuario.obtener_user_data(user, True)
            cuenta['metricas'] = gestor_usuario.obtener_metricas_kas(user['public_metrics'])
        # Obtiene la info del usuario
        today = datetime.now()
        usuario = {
            'nombre': 'Carlos Morocho',
            'fecha': today.strftime("%Y-%m-%d"),
            'hora': today.strftime("%H:%M %p")
        }
        # Obtiene la info de los tweets
        file_name = gestor_reportes.generar_accion_reporte(id_cuenta, accion, cuenta, usuario)
        return send_file(file_name, attachment_filename='report_tweets.pdf')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

