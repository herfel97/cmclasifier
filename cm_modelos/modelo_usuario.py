"""
    C&M - Modelos Usuarios
    ====================
    Modelos para las tablas de gestion de Usuarios.
    :autor @cmorocho
"""
from cm_modelos import ModelBaseCM
from sqlalchemy.orm import relation
from sqlalchemy import Column, String, Integer, ForeignKey, Numeric, Boolean


class Usuario(ModelBaseCM):
    """
        Modelo Usuario
    """
    __tablename__ = 'cm_usuarios'

    nombre = Column(String(400), nullable=False)
    correo = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    es_admin = Column(Boolean, default=False)
    cuentas = relation('UsuarioCuenta', backref="usuario", lazy=True)


class CuentaClase(ModelBaseCM):
    """
        Modelo Usuario Cuentas Clase
    """

    __tablename__ = 'cm_cuentas_clases'

    cuenta_id = Column(String(100), nullable=False)
    nombre = Column(String(100), nullable=False)
    min_score = Column(Numeric, default=0.0)
    max_score = Column(Numeric, default=100)
    descripcion = Column(String(500))
    color = Column(String(500), default="rgb(29, 155, 240)")
    default = Column(Boolean, default=False)
    clasificaciones = relation('ClaseTweet', backref="clase", lazy=True)


class CuentaAccion(ModelBaseCM):
    """
        Modelo Usuario Cuentas Acciones
    """

    __tablename__ = 'cm_cuentas_acciones'

    cuenta_id = Column(String(100), nullable=False)
    codigo = Column(String(50), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    favorito = Column(Boolean, default=False)
    json_filtros = Column(String(), default="{}")
    json_reporte = Column(String(), default="{}")


class UsuarioCuenta(ModelBaseCM):
    """
        Modelo Usuario Cuentas
    """

    __tablename__ = 'cm_usuarios_cuentas'

    usuario_id = Column(Integer, ForeignKey('cm_usuarios.id', ondelete='CASCADE'), nullable=False)
    cuenta_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)

