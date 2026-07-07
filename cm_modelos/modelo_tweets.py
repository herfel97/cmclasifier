"""
    C&M - Modelos Tweets
    ====================
    Modelos para las tablas de gestion de Tweets.
    :autor @cmorocho
"""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import relation

from cm_modelos import ModelBaseCM


class EntidadTweet(ModelBaseCM):
    """
     Modelo mapeo tabla Entidad Tweets
    """
    __tablename__ = 'cm_entidades_tweets'

    tweet_id = Column(Integer, ForeignKey('cm_tweets.id', ondelete='CASCADE'), nullable=False)
    tipo = Column(String(50), nullable=False)
    label = Column(String(400), nullable=False)
    valor = Column(String(400), nullable=False)

    def __init__(self, tipo, label, valor):
        self.tipo = tipo
        self.label = label
        self.valor = valor


class ClaseTweet(ModelBaseCM):
    """
        Modelo mapeo tabla Clase Tweets
    """
    __tablename__ = 'cm_clases_tweets'

    tweet_cuenta_id = Column(Integer, ForeignKey('cm_tweets_cuentas.id', ondelete='CASCADE'), nullable=False)
    cuenta_clase_id = Column(Integer, ForeignKey('cm_cuentas_clases.id'), nullable=False)
    score = Column(Numeric, nullable=False)
    is_selected = Column(Boolean, default=False)

    def __init__(self, cuenta_clase_id, score, is_selected=False):
        self.cuenta_clase_id = cuenta_clase_id
        self.score = score
        self.is_selected = is_selected


class CuentaTweet(ModelBaseCM):
    """
     Modelo mapeo tabla Cuenta Tweets
    """
    __tablename__ = 'cm_tweets_cuentas'

    tweet_id = Column(Integer, ForeignKey('cm_tweets.id', ondelete='CASCADE'), nullable=False)
    cuenta_id = Column(String(100), nullable=False)
    tipo = Column(String(10), nullable=False)
    origen = Column(String(100), nullable=False)

    clasificaciones = relation('ClaseTweet', backref="cuenta_tweet", lazy=True)

    def __init__(self, cuenta_id, tipo, origen, clasificaciones):
        self.cuenta_id = cuenta_id
        self.tipo = tipo
        self.origen = origen
        self.clasificaciones = clasificaciones


class Tweet(ModelBaseCM):
    """
     Modelo mapeo tabla Tweets
    """
    __tablename__ = 'cm_tweets'

    # Atributos
    codigo = Column(String(100), nullable=False)
    autor_id = Column(String(100), nullable=False)
    fecha = Column(DateTime(True), nullable=False)
    texto = Column(String(600), nullable=False)

    # Relaciones
    cuentas = relation('CuentaTweet', backref="tweet", lazy=True)
    entidades = relation('EntidadTweet', backref="tweet", lazy=True)

    def __init__(self, codigo, autor_id, is_reply, texto, fecha):
        self.codigo = codigo
        self.autor_id = autor_id
        self.texto = texto
        self.is_reply = is_reply
        self.fecha = fecha

    def __str__(self):
        return f'( {self.codigo} ) {self.texto}'


