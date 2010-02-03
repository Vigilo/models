# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
"""Modèle pour la table ImpactedPath."""
from __future__ import absolute_import

from sqlalchemy import ForeignKey, Column
from sqlalchemy.orm import relation
from sqlalchemy.types import Integer

from .vigilo_bdd_config import bdd_basename, DeclarativeBase

__all__ = ('ImpactedPath', )

class ImpactedPath(DeclarativeBase, object):
    """
    Cette classe contient les données relatives à un chemin d'impactes.

    @ivar idpath: Identifiant auto-généré du chemin.
    @ivar impacted_hls: Liste des L{HighLevelService} impactés présents
        sur le chemin.
    @ivar idsupitem: Identifiant de l'élément supervisé à l'origine du
        chemin d'impactes.
    @ivar supitem: Instance de l'élément supervisé à l'origine du chemin
        d'impactes.
    """

    __tablename__ = bdd_basename + 'impactedpath'

    idpath = Column(
        Integer,
        primary_key=True, autoincrement=True,
    )

    impacted_hls = relation('ImpactedHLS', back_populates='path', lazy=True)

    idsupitem = Column(
        Integer,
        ForeignKey(
            bdd_basename + 'supitem.idsupitem',
            ondelete='CASCADE', onupdate='CASCADE',
        ),
        nullable=False,
    )

    supitem = relation('SupItem')

