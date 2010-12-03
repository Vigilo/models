# -*- coding: utf-8 -*-
"""Test suite for DependencyGroup class"""
from vigilo.models.tables import DependencyGroup, Host
from vigilo.models.session import DBSession

from controller import ModelTest

class TestDependencyGroup(ModelTest):
    """Test de la table DependencyGroup."""

    klass = DependencyGroup

    attrs = {
        'operator': u'+',
    }

    def __init__(self):
        ModelTest.__init__(self)

    def do_get_dependencies(self):
        """Generate some data for the test"""
        ModelTest.do_get_dependencies(self)
        host = Host(
            name=u'myhost',
            checkhostcmd=u'halt -f',
            snmpcommunity=u'public',
            description=u'My Host',
            hosttpl=u'template',
            address=u'127.0.0.1',
            snmpport=u'1234',
            weight=42,
        )
        DBSession.add(host)

        return dict(dependent=host)
