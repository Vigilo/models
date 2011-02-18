# -*- coding: utf-8 -*-
"""
Ajoute un index sur les noms de fichiers ConfFile, pour gagner en performances.
"""

from vigilo.models.session import DBSession, ClusteredDDL
from vigilo.models.configure import DB_BASENAME
from vigilo.models import tables

def upgrade(migrate_engine, cluster_name):
    ClusteredDDL(
        [
            "ALTER TABLE %(fullname)s ALTER COLUMN name TYPE varchar(512)",
        ],
        cluster_name=cluster_name,
        # La modification n'impacte pas la réplication
        # vers VigiReport (set n°3).
        cluster_sets=[2],
        # Le nom de la contrainte dépend du préfixe utilisé.
        context={
            'db_basename': DB_BASENAME,
        }
    ).execute(DBSession, tables.ConfFile.__table__)
