"""
    C&M - Modelos
    ===============
    Inicialización de los Modelos
    :autor @cmorocho
"""
from flask_sqlalchemy import Model, SQLAlchemy, _QueryProperty
from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

from common_utils import get_database_session


class Auditoria(Model):
    """
        Modelo abstracto auditoria registro
    """
    __abstract__ = True

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    activo = Column('activo', Boolean, default=True)
    usuario_registro = Column('usuario_registro', Integer, default=0)
    fecha_registro = Column('fecha_registro', DateTime, default=func.now())

    def save(self, session=None):
        """
        Persiste el registro
        :param session:
        :return:
        """
        # Verifica si existe la conexion
        session_a = (session or get_database_session())
        if self.id:  # Verficia si tiene ID
            # Actualiza los datos del Modelo
            update_fileds = dict(self.__dict__)
            update_fileds.pop('_sa_instance_state')
            self.update(update_fileds, session_a)
        else:
            session_a.add(self)
            session_a.commit()
            if not session:
                session_a.close()
        return self

    def update(self, fileds, session=None):
        """
        Actualiza el registro
        :param fileds:
        :param session:
        :return:
        """
        # Verifica si existe la conexion
        session_a = (session or get_database_session())
        fileds.pop('id')
        # Actualiza el modelo
        session.query(self.__class__) \
            .filter_by(id=self.id).update(fileds)
        session.commit()
        if not session:
            session_a.close()

    def delete(self, session=None):
        """
        Elimina el registro
        :param session:
        :return:
        """
        # Verifica si existe la conexion
        session_a = (session or get_database_session())
        # Actualiza el modelo
        session_a.query(self.__class__) \
            .filter_by(id=self.id).delete()
        session_a.commit()
        if not session:
            session_a.close()


# Modelo CM
ModelBaseCM = declarative_base(cls=Auditoria, name='ModelCM')


class SQLAlchemyCM(SQLAlchemy):

    def __init__(self, app):
        super(SQLAlchemyCM, self).__init__(app)
        self.Model = ModelBaseCM
        self.Model.query_class = self.Query
        self.Model.query = _QueryProperty(self)
        self.create_all()
