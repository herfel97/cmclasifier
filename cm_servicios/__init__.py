"""
    C&M - Servicios
    ===============
    Inicialización de los Servicios
    :autor @cmorocho
"""
from flask import Blueprint
from cm_gestores import gestor_usuario
from cm_servicios import servicio_usuario as usr_serv
from cm_servicios import servicio_tweets as twt_serv
from cm_servicios import servicio_reportes as rep_serv

URLS = [
    # APIs Usuario
    ('/usuario/autenticar', ['POST'], usr_serv.api_autenticar_usuario),
    ('/usuario/agregar/cuenta', ['POST'], usr_serv.api_agregar_cuenta_usuario),
    ('/usuario/obtener/cuentas/<string:modo>', ['GET'], usr_serv.api_obtener_cuentas_usuario),
    ('/usuario/buscar/por/id/<string:id_cuenta>', ['GET'], usr_serv.api_buscar_cuenta_por_id),
    ('/usuario/buscar/por/nombre/<string:username>', ['GET'], usr_serv.api_buscar_cuenta_por_nombre),
    ('/usuario/obtener/todos', ['GET'], usr_serv.api_obtener_usuarios_cuentas),
    ('/usuario/agregar/registro', ['POST'], usr_serv.api_agregar_usuario_cuenta),
    ('/usuario/eliminar/<int:usuario_id>', ['DELETE'], usr_serv.api_eliminar_usuario_cuenta),
    ('/usuario/obtener/clases/<string:id_cuenta>', ['GET'], usr_serv.api_obtener_clases_cuenta),
    ('/usuario/agregar/clase/<string:id_cuenta>', ['POST'], usr_serv.api_agregar_clase_cuenta),
    ('/usuario/eliminar/clase/<int:id_clase>', ['DELETE'], usr_serv.api_eliminar_clase_cuenta),
    ('/usuario/obtener/acciones/<string:id_cuenta>', ['GET'], usr_serv.api_obtener_acciones_cuenta),
    ('/usuario/agregar/accion/<string:id_cuenta>', ['POST'], usr_serv.api_agregar_accion_cuenta),
    ('/usuario/eliminar/accion/<int:id_accion>', ['DELETE'], usr_serv.api_eliminar_accion_cuenta),
    ('/usuario/favorito/accion/<int:id_accion>', ['GET'], usr_serv.api_favorito_accion_cuenta),
    ('/usuario/chat/mensaje/<string:id_cuenta>', ['POST'], usr_serv.api_enviar_mensaje),

    # APIs Tweets
    ('/tweets/total/valores/<string:id_cuenta>', ['GET'], twt_serv.api_obtener_total_valores),
    ('/tweets/interacciones/<string:id_cuenta>', ['GET'], twt_serv.api_obtener_interacciones),
    ('/tweets/clasificaciones/<string:id_cuenta>', ['POST'], twt_serv.api_obtener_clasificaciones),
    ('/tweets/por/filtro/<string:id_cuenta>/<int:pagina>', ['POST'], twt_serv.api_obtener_tweets_filtro),
    ('/tweets/obtener/data/<string:id_cuenta>/<int:id_tweet>', ['GET'], twt_serv.api_obtener_data_tweet),
    ('/tweets/interacciones/cuentas/<string:id_cuenta>', ['GET'], twt_serv.api_obtener_interacciones_cuentas),
    ('/tweets/por/tipos/<string:id_cuenta>', ['POST'], twt_serv.api_obtener_tweets_por_tipos),

    # APIs Reportes
    ('/reportes/generar/por/accion/<string:id_cuenta>', ['POST'], rep_serv.generar_por_accion)
]


class ApiRestCM(Blueprint):

    def __init__(self):
        super(ApiRestCM, self).__init__("CM Api Rest", __name__, url_prefix='/api')
        for url in URLS:
            rule, methods, view_func = url
            self.add_url_rule(rule=rule, methods=methods, view_func=view_func)

    @staticmethod
    def crear_usuario_admin(usuario):
        """
        Crea el usuario admin
        :return:
        """
        return gestor_usuario.agregar_usuario_cuenta(0, usuario, True)

    @staticmethod
    def obtener_usuario_por_id(id_usuario):
        """
        Obtiene el usuario logeado
        :return:
        """
        return gestor_usuario.obtener_usuario_por_id(id_usuario)

    @staticmethod
    def verificar_cuenta_usuario(id_usuario, id_cuenta):
        """
        Verifica que el usuario tiene asociado la cuenta
        :param id_usuario:
        :param id_cuenta:
        :return:
        """
        # Obtiene las cuentas asociadas al usuario
        items = gestor_usuario.obtener_cuentas_usuario(
            id_usuario
        )  # Valida que tenga la cuenta
        cuentas = {}
        for item in items:
            cuentas[item['cuenta_id']] = item
        # Retorna la cuenta
        return cuentas.get(id_cuenta)
