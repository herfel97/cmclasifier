"""
    C&M - Main
    ==========
    Inicialización de la aplicacion
    :autor @cmorocho
"""

from flask import Flask
from chat_bot import ChatBotAssistan
from cm_modelos import SQLAlchemyCM
from cm_servicios import ApiRestCM
from live_streaming import TweetLiveCM
from clasificador import ClasificationModel


class AppTweetCM(Flask):

    cm_bd_app = None
    cm_api_app = None
    cm_live_app = None
    cm_chat_bot = None
    cm_clasificador = None

    def current_session(self):
        return self.cm_bd_app.session

    def init_app(self):
        # Inicializa la BD
        self.cm_bd_app = SQLAlchemyCM(self)
        # Inicializa utilitarios
        self.cm_api_app = ApiRestCM()
        self.cm_chat_bot = ChatBotAssistan()
        self.cm_clasificador = ClasificationModel()
        self.register_blueprint(self.cm_api_app)
        # Inicializa el LIVE
        self.cm_live_app = TweetLiveCM(self)

    def create_user_admin(self):
        """
        Crea el usuario admin
        :return:
        """
        with self.app_context():
            self.cm_api_app.crear_usuario_admin({
                'nombre': "Carlos Morocho",
                'correo': "cmorocho_new@outlook.com",
                'password': 'admin1234',
                'cuentas': [{'cuenta_id': '1340073922902061058', 'username': '@cmorocho4'}],
            })

    def run_live(self, **kwargs):
        self.cm_live_app.run(self, **kwargs)


# Crea la App
cm_app = AppTweetCM(__name__)
cm_app.config.from_pyfile("settings.py")

# Arranca la app
if __name__ == '__main__':
    cm_app.init_app()
    # cm_app.create_user_admin()  # Solo se debe ejecutar una vez
    cm_app.run_live(host='0.0.0.0', port=5000)
