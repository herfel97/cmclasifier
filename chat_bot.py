"""
    C&M - Chat Boot
    ========================
    Gestor del Chat Boot servicio IBM Watson Assistant
    :autor @cmorocho
"""
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from settings import API_KEY_ASSISTANT_SERVICE, API_URL_ASSISTANT_SERVICE, ASSISTANT_ID


class ChatBotAssistan(object):

    assistant = None

    def __init__(self):
        # Iniciamos el servicio de Watson Assistant
        self.assistant = AssistantV2(
            version='2018-09-20',
            authenticator=IAMAuthenticator(API_KEY_ASSISTANT_SERVICE)
        )
        self.assistant.set_service_url(API_URL_ASSISTANT_SERVICE)

    def obtener_session(self):
        """
        Obtieme la session del usuario
        :return:
        """
        # Crea la session para inciar el chat
        return self.assistant.create_session(ASSISTANT_ID) \
            .get_result().get('session_id')

    def iniciar_chat_boot(self, session_id):
        """
        Inicializamos el servicio de char boot
        :param session_id:
        :return:
        """
        # Obtiene el mensaje de binvenida
        return self.assistant.message(ASSISTANT_ID, session_id) \
            .get_result().get('output').get('generic')

    def enviar_mensaje(self, session_id, mensaje):
        """
        Envia y obtiene las respuestas del watson asist
        :param session_id:
        :param mensaje:
        :return:
        """
        # Arma el contexto
        inputs = {'message_type': 'text', 'text': mensaje}
        context = {
            "skills": {
                "main skill": {
                    "user_defined": {'idioma': 'espanol'}
                }
            },
        }
        # Consulta el servicio de watson assistant
        mensajes = self.assistant.message(ASSISTANT_ID, session_id, input=inputs, context=context) \
            .get_result().get('output').get('generic')
        return mensajes


if __name__ == '__main__':
    # Iniciamos el servicio de Watson Assistant
    pass
