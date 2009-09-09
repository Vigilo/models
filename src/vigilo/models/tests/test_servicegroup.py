# -*- coding: utf-8 -*-
"""Test suite for ServiceGroup class"""
from vigilo.models import Service, Group, ServiceGroup
from vigilo.models.tests import ModelTest
from vigilo.models.session import DBSession

class TestServiceGroup(ModelTest):
    """Test de la table ServiceGroup"""

    klass = ServiceGroup
    attrs = {}

    def do_get_dependencies(self):
        """Generate some data for the test"""

        DBSession.add(Service(name = u"monservice"))
        DBSession.add(Group(name = u"mongroupe"))
        DBSession.flush()
        return dict(servicename = u"monservice", groupname = u"mongroupe")

    def __init__(self):
        ModelTest.__init__(self)
