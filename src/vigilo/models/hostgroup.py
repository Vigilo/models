# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table HostGroup"""
from __future__ import absolute_import

from sqlalchemy import ForeignKey, Column
from sqlalchemy.types import Unicode
from sqlalchemy.orm import relation

from .vigilo_bdd_config import bdd_basename, DeclarativeBase

__all__ = ('HostGroup', )

class HostGroup(DeclarativeBase, object):

    __tablename__ = bdd_basename + 'hostgroup'

    hostname = Column(
        Unicode(255),
        ForeignKey(bdd_basename + u'host.name'),
        primary_key=True, nullable=False,
        info={'rum': {'field': 'Text'}})

    groupname = Column(
        Unicode(255),
        ForeignKey(bdd_basename + u'group.name'),
        primary_key=True, nullable=False,
        info={'rum': {'field': 'Text'}})

#    host = relation('Host', backref='host_groups')
#    group = relation('Group', backref='hosts')

    def __init__(self, **kwargs):
        """Initialise un groupe d'hôtes."""
        DeclarativeBase.__init__(self, **kwargs)
