# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table Permissions"""
from __future__ import absolute_import

from sqlalchemy.orm import mapper
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import Integer, UnicodeText
from sqlalchemy.orm import relation

from .vigilo_bdd_config import bdd_basename, DeclarativeBase, metadata
from .usergroup import UserGroup

__all__ = ('Permission', )

group_permission_table = Table('usergrouppermissions', metadata,
    Column('groupname', UnicodeText, ForeignKey(
        bdd_basename + 'usergroup.group_name',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('idpermission', Integer, ForeignKey(
        bdd_basename + 'permission.idpermission',
        onupdate="CASCADE", ondelete="CASCADE"))
)

class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.
    Only the ``permission_name`` column is required by :mod:`repoze.what`.
    """

    __tablename__ = bdd_basename + 'permission'

    idpermission = Column(
        Integer,
        autoincrement=True,
        primary_key=True)

    # TG2 expects this name.
    permission_name = Column(
        UnicodeText(),
        unique=True,
        nullable=False)

    groups = relation('UserGroup', secondary=group_permission_table,
                      backref='permissions')

    def __unicode__(self):
        return self.permission_name
