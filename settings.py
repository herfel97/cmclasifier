##########################################################
# This is a sample flask.cfg for developing a Flask application
##########################################################
import os

# Get the folder of the top-level directory of this project
BASEDIR = os.path.dirname(__file__)

# FLASK VARIABLES
SECRET_KEY = '(pebch@1kn(xs)ddc580mjd9q%lm5a=(6%#=s145721l3$km-_'
FLASK_ENV = 'development'
FLASK_DEBUG = True
WTF_CSRF_ENABLED = True

# TWEETER KEYS
BEARER_TOKEN = os.getenv(
    "BEARER_TOKEN",
    "AAAAAAAAAAAAAAAAAAAAAH81KwEAAAAAuRCx0lLkln4RyfA5euWvZ0PNx9k%3D5MTHHrAs1or71Tml53AUryfW9qMoUpPWQUIIHRzIml7Bp4Y51w"
)
#BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABfTbQEAAAAAiyw2%2Bwpa8DYfGs4ojhnHkXKUS6E%3DSEp4c3HypF8lGBvDC4szruWU3KZVlHrJq4JwsXilV5PKXDApdg"
#BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAHXKZAEAAAAAfxNhzkF0pp3WSRNS6zETHnpz9YY%3DgLxerMtVdnBpQNjIiFuZl0RmjS1hbHO2XC0Dalxn2XxguLkGHX"
# SQLAlchemy
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_NAME = os.getenv("DB_NAME", "cm_clasificador_2")
DB_HOST_PORT = os.getenv("DB_HOST_PORT", "localhost:5432")
SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST_PORT}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False
# SQLALCHEMY_POOL_TIMEOUT = 1.0
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"options": "-c timezone=America/Bogota"}}

# FORMAT
URL_API_TWITTER = "https://api.twitter.com/2"
FORMAT_DATETIME = '%Y-%m-%d %H:%M %p'
FORMAT_DATE = '%Y-%m-%d'
FORMAT_TIME = '%H:%M:%S'
MAX_FILAS_POR_PAGINA = 50

ASSISTANT_ID = os.getenv("ASSISTANT_ID", "03e63efd-bf67-4862-baeb-465d7c01f7d8")
API_KEY_ASSISTANT_SERVICE = os.getenv("API_KEY_ASSISTANT_SERVICE", "CNu68PMoTLa019TmCDpatrVC6eL97SyQSuLY544xgMjf")
API_URL_ASSISTANT_SERVICE = os.getenv("API_URL_ASSISTANT_SERVICE", "https://api.us-south.assistant.watson.cloud.ibm.com")
