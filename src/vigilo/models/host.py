# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table Host"""
from __future__ import absolute_import

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText
from sqlalchemy.orm import relation
from sqlalchemy.ext.associationproxy import association_proxy

from .vigilo_bdd_config import bdd_basename, DeclarativeBase, metadata

__all__ = ('Host', )

class Host(DeclarativeBase):
    __tablename__ = bdd_basename + 'host'

    name = Column(
        UnicodeText(),
        index=True,primary_key=True, nullable=False)
    checkhostcmd = Column(
        UnicodeText(),
        nullable=False)
    community = Column(
        UnicodeText(),
        nullable=False)
    fqhn = Column(
        UnicodeText(),
        nullable=False)
    hosttpl = Column(
        UnicodeText(),
        nullable=False)
    mainip = Column(
        UnicodeText(),
        nullable=False)
    port = Column( Integer(), nullable=False)
    snmpoidsperpdu = Column( Integer())
    snmpversion = Column(
        UnicodeText())

    groups = association_proxy('host_groups', 'groups')

    def __init__(self, name, checkhostcmd = '', community = '', fqhn = '',
            hosttpl = '', mainip = '', port = 0, snmpoidsperdu = 0,
            snmpversion = ''):
        self.name = name
        self.checkhostcmd = checkhostcmd
        self.community = community
        self.fqhn = fqhn
        self.hosttpl = hosttpl
        self.mainip = mainip
        self.port = port
        self.snmpoidsperdu = snmpoidsperdu
        self.snmpversion = snmpversion


