# -*- coding: utf-8 -*-
"""Modèle pour la table Ventilation."""
from sqlalchemy import Column
from sqlalchemy.types import Unicode, Integer
from sqlalchemy.orm import relation, backref

from vigilo.models.configure import DeclarativeBase, ForeignKey
from vigilo.models.host import Host
from vigilo.models.vigiloserver import VigiloServer
from vigilo.models.application import Application

__all__ = ('CustomGraphView', )

class Ventilation(DeclarativeBase, object):
    """
    Gestion de la ventilation des hôtes supervisés, c'est-à-dire que cette
    classe gère la répartition des hosts par serveur Vigilo et par groupe
    d'applications.

    @ivar idhost: Identifiant de l'hôte à ventiler.
    @ivar host: Instance de l'hôte à ventiler.
    @ivar idvigiloserver: Identifiant du serveur Vigilo sur lequel
        l'hôte sera ventilé.
    @ivar vigiloserver: Instance du serveur Vigilo sur lequel l'hôte
        sera ventilé.
    @ivar idapp: Identifiant de l'L{Application} installée.
    @ivar application: Instance de l'L{Application} installée.
    """
    
    __tablename__ = 'ventilation'

    idhost = Column(
        Integer,
        ForeignKey(
            Host.idhost,
            onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True,
        autoincrement=False,
    )

    host = relation('Host')

    idvigiloserver = Column(
        Integer,
        ForeignKey(
            VigiloServer.idvigiloserver,
            onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True,
        autoincrement=False,
    )

    vigiloserver = relation('VigiloServer')

    idapp = Column(
        Integer,
        ForeignKey(
            Application.idapp,
            onupdate="CASCADE", ondelete="CASCADE"),
        index=True,
        primary_key=True,
        autoincrement=False,
    )

    application = relation('Application')

    def __init__(self, **kwargs):
        """Initialise une association ventilation."""   
        super(Ventilation, self).__init__(**kwargs)

