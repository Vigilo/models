# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table UserGroup"""
from __future__ import absolute_import

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import UnicodeText
from sqlalchemy.orm import relation

from .vigilo_bdd_config import bdd_basename, DeclarativeBase, metadata

__all__ = ('UserGroup', )

USER_GROUP_TABLE = Table(
    bdd_basename + 'usertousergroups', metadata,
    Column('username', UnicodeText, ForeignKey(
                bdd_basename + 'user.user_name',
                onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True),
    Column('groupname', UnicodeText, ForeignKey(
                bdd_basename + 'usergroup.group_name',
                onupdate="CASCADE", ondelete="CASCADE"),
            primary_key=True)
)

class UserGroup(DeclarativeBase, object):
    """User groups, used eg. to organize users by services, privileges, etc."""

    __tablename__ = bdd_basename + 'usergroup'

    # TG2 expects this name.
    group_name = Column(
        UnicodeText(),
        primary_key=True)

    users = relation('User', secondary=USER_GROUP_TABLE, backref='usergroups')

    def __init__(self, **kwargs):
        DeclarativeBase.__init__(self, **kwargs)

    def __unicode__(self):
        return self.group_name

    @classmethod
    def by_group_name(cls, group_name):
        """Return the group object whose group name is ``group_name``."""
        return DBSession.query(cls).filter(cls.group_name==group_name).first()

