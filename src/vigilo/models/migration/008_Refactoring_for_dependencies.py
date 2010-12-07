# -*- coding: utf-8 -*-
"""
La gestion des dépendances entre les éléments supervisés
a été revue afin de permettre une plus grande souplesse.
"""

from vigilo.models.session import DBSession, ClusteredDDL
from vigilo.models.configure import DB_BASENAME
from vigilo.models import tables

from vigilo.models.session import PrefixedTables, ForeignKey
from vigilo.models.tables.supitem import SupItem
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode

from sqlalchemy.ext.declarative import declarative_base
DeclarativeBase = declarative_base(metaclass=PrefixedTables)

class DependencyGroup(DeclarativeBase, object):
    """Groupe de dépendances, réunies par un opérateur."""
    __tablename__ = 'dependencygroup'

    idgroup = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    operator = Column(
        Unicode(1),
        nullable=False,
    )

    iddependent = Column(
        Integer,
        ForeignKey(
            SupItem.idsupitem,
            ondelete='CASCADE',
            onupdate='CASCADE',
        ),
        nullable=False,
    )

def upgrade(migrate_engine, cluster_name):
    # Création de la nouvelle table DependencyGroup.
    DeclarativeBase.metadata.create_all(
        bind=DBSession.bind,
        tables=[DependencyGroup.__table__]
    )

    supitem_refs = [
        ('lowlevelservice', 'idservice'),
        ('highlevelservice', 'idservice'),
        ('mapservicelink', 'idref'),
        ('mapnodeservice', 'idservice'),
    ]

    hls_refs = [
        ('impactedhls', 'idhls'),
        ('hlshistory', 'idhls'),
    ]

    ClusteredDDL(
        # Suppression des contraintes référentielles vers Service...
        [
            "ALTER TABLE %%(db_basename)s%(table)s DROP CONSTRAINT "
                "%%(db_basename)s%(table)s_%(field)s_fkey" % {
                    'table': table,
                    'field': field,
                } for (table, field) in (supitem_refs + hls_refs)
        ] +

        # ...et ajout de contraintes référentielles vers HighLevelService...
        [
            "ALTER TABLE %%(db_basename)s%(table)s ADD CONSTRAINT "
                "%%(db_basename)s%(table)s_%(field)s_fkey "
                "FOREIGN KEY(%(field)s) REFERENCES "
                "%%(db_basename)shighlevelservice(idservice) "
                "ON UPDATE CASCADE ON DELETE CASCADE" % {
                    'table': table,
                    'field': field,
                } for (table, field) in hls_refs
        ] +

        # ...ou SupItem directement selon les cas.
        [
            "ALTER TABLE %%(db_basename)s%(table)s ADD CONSTRAINT "
                "%%(db_basename)s%(table)s_%(field)s_fkey "
                "FOREIGN KEY(%(field)s) REFERENCES "
                "%%(db_basename)ssupitem(idsupitem) "
                "ON UPDATE CASCADE ON DELETE CASCADE" % {
                    'table': table,
                    'field': field,
                } for (table, field) in supitem_refs
        ] +

        # Autres modifications.
        [
            # Suppression de l'ancienne table Service.
            "DROP TABLE %(db_basename)s%(old_table)s",

            # Suppression des contraintes dans Dependency.
            "ALTER TABLE %(fullname)s DROP CONSTRAINT "
                "%(db_basename)sdependency_pkey",
            "ALTER TABLE %(fullname)s DROP CONSTRAINT "
                "%(db_basename)sdependency_idsupitem1_fkey",
            "ALTER TABLE %(fullname)s DROP CONSTRAINT "
                "%(db_basename)sdependency_idsupitem2_fkey",

            # Modification des champs dans Dependency.
            "ALTER TABLE %(fullname)s RENAME COLUMN idsupitem1 TO idgroup",
            "ALTER TABLE %(fullname)s RENAME COLUMN idsupitem2 TO idsupitem",

            # Ajout des nouvelles contraintes dans Dependency.
            "ALTER TABLE %(fullname)s ADD CONSTRAINT %(fullname)s_idgroup_fkey "
                "FOREIGN KEY(idgroup) REFERENCES %(db_basename)sdependencygroup(idgroup) "
                "ON UPDATE CASCADE ON DELETE CASCADE",
            "ALTER TABLE %(fullname)s ADD CONSTRAINT %(fullname)s_idsupitem_fkey "
                "FOREIGN KEY(idsupitem) REFERENCES %(db_basename)ssupitem(idsupitem) "
                "ON UPDATE CASCADE ON DELETE CASCADE",
            "ALTER TABLE %(fullname)s ADD PRIMARY KEY (idgroup, idsupitem)",
        ],
        cluster_name=cluster_name,
        cluster_sets=[2],
        # Le nom de la contrainte dépend du préfixe utilisé.
        context={
            'db_basename': DB_BASENAME,
            'old_table': 'service',
        }
    ).execute(DBSession, tables.Dependency.__table__)

    print   "ATTENTION: Though the schema migration completed successfully,\n" \
            "you should re-deploy your configuration to finish the migration."