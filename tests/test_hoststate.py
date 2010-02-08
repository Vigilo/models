# -*- coding: utf-8 -*-
"""Test suite for State class"""
from vigilo.models import State, Host
from vigilo.models.configure import DBSession

from datetime import datetime

from controller import ModelTest

class TestHostState(ModelTest):
    """Test de la table State avec un Host"""

    klass = State
    attrs = {
        # On ne peut pas utiliser StateName.statename_to_value ici
        # car le modèle n'est pas encore créé lorsque ce code est
        # exécuté.
        'state': 3, # = WARNING
        'attempt': 42,
        'timestamp': datetime.now(),
        'message': 'Foo!',
    }

    def __init__(self):
        """Initialise le test."""
        ModelTest.__init__(self)

    def do_get_dependencies(self):
        """Génère les dépendances de cette instance."""
        # Insère les noms d'états dans la base de données.
        ModelTest.do_get_dependencies(self)

        host = Host(
            name=u'myhost',
            checkhostcmd=u'halt -f',
            snmpcommunity=u'public',
            description=u'My Host',
            hosttpl=u'template',
            mainip=u'127.0.0.1',
            snmpport=u'1234',
            weight=42,
        )
        DBSession.add(host)

        DBSession.flush()
        return dict(supitem=host)

