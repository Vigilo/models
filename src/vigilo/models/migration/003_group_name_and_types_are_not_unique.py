# -*- coding: utf-8 -*-
"""
Supprime la contrainte d'unicité sur un nom + type de groupe.
Les groupes sont désormais organisés en arborescence et le même nom
peut donc apparaître à plusieurs endroits dans cette arborescence.
"""

from vigilo.models.session import DBSession, MigrationDDL
from vigilo.models.configure import DB_BASENAME
from vigilo.models import tables

def upgrade(migrate_engine, actions):
    MigrationDDL(
        [
            "ALTER TABLE %(fullname)s DROP CONSTRAINT "
                "%(db_basename)sgroup_grouptype_key",
        ],
        # Le nom de la contrainte dépend du préfixe utilisé.
        context={
            'db_basename': DB_BASENAME,
        }
    ).execute(DBSession, tables.Host.__table__)

    # Nécessite une mise à jour de VigiReport.
    actions.upgrade_vigireport = True
