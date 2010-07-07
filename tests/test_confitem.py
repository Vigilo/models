# -*- coding: utf-8 -*-
"""Test suite for ConfItem class"""
from nose.tools import assert_equals

from vigilo.models.session import DBSession
from vigilo.models.tables import Host, LowLevelService
from vigilo.models.tables import ConfItem
from controller import ModelTest

class TestServiceConfItem(ModelTest):
    """Unit test case for the ``ConfItem`` model."""

    klass = ConfItem

    attrs = dict(
        name = u'retry_interval',
        value = u"4"
    )

    def __init__(self):
        """Initialisation du test."""
        ModelTest.__init__(self)

    def do_get_dependencies(self):
        """Insertion de données dans la base préalable aux tests."""
        ModelTest.do_get_dependencies(self)

        host = Host(
            name=u'myhost',
            checkhostcmd=u'halt -f',
            snmpcommunity=u'public',
            description=u'My Host',
            hosttpl=u'template',
            address=u'127.0.0.1',
            snmpport=1234,
            weight=42,
        )
        DBSession.add(host)

        service = LowLevelService(
            host=host,
            servicename=u'myservice',
            command=u'halt',
            op_dep=u'+',
            weight=42,
        )
        DBSession.add(service)
        DBSession.flush()
        
        return dict(supitem=service,)
    
    def test_get_by_host_service_confitem_name(self):
        ob = ConfItem.by_host_service_confitem_name(u'myhost', u'myservice', u'retry_interval')
        assert_equals('4', ob.value)
        


class TestHostConfItem(ModelTest):
    """Unit test case for the ``ConfItem`` model."""

    klass = ConfItem

    attrs = dict(
        name = u"check_interval",
        value = u"5"
    )

    def __init__(self):
        """Initialisation du test."""
        ModelTest.__init__(self)

    def do_get_dependencies(self):
        """Insertion de données dans la base préalable aux tests."""
        ModelTest.do_get_dependencies(self)

        host = Host(
            name=u'myhost',
            checkhostcmd=u'halt -f',
            snmpcommunity=u'public',
            description=u'My Host',
            hosttpl=u'template',
            address=u'127.0.0.1',
            snmpport=1234,
            weight=42,
        )
        DBSession.add(host)
        
        return dict(supitem=host,)
    
    def test_get_by_host_confitem_name(self):
        ob = ConfItem.by_host_confitem_name(u'myhost', u'check_interval')
        assert_equals('5', ob.value)
