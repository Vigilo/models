# -*- coding: utf-8 -*-
"""
Script permettant de purger périodiquement la base de données
des événements associés à VigiBoard.
"""

import sys
import time
import sqlalchemy.sql.functions as sqlfuncs
from sqlalchemy import types as sqltypes
import transaction
from datetime import datetime
from optparse import OptionParser

__all__ = (
    'clean_vigiboard',
)

class pg_database_size(sqlfuncs.GenericFunction):
    """
    Fonction permettant d'utiliser l'expression "pg_database_size"
    de PostgreSQL afin de déterminer la taille occupée sur le disque
    par la base de données.

    @note: Cette fonction est spécifique à PostgreSQL.
    """
    __return_type__ = sqltypes.Integer

    def __init__(self, arg, **kwargs):
        super(pg_database_size, self).__init__(args=[arg], **kwargs)

def clean_vigiboard(*args):
    """
    Cette fonction supprime les événements les plus anciens
    des tables utilisées par VigiBoard.
    """

    from vigilo.common.gettext import translate
    _ = translate(__name__)

    parser = OptionParser()
    parser.add_option("-d", "--days", action="store", dest="days",
        type="int", default=None, help=_("Remove closed events which are "
        "at least DAYS old. DAYS must be a positive non-zero integer."))
    parser.add_option("-s", "--size", action="store", dest="size",
        type="int", default=None, help=_("Remove closed events, starting "
        "with the oldest ones, when the Vigilo database starts occupying "
        "more then SIZE bytes. SIZE must be a positive non-zero integer."))
    parser.add_option("-c", "--config", action="store", dest="config",
        type="string", default=None, help=_("Load configuration from "
        "this file."))

    (options, args) = parser.parse_args()

    from vigilo.common.conf import settings
    if options.config:
        settings.load_file(options.config)
    else:
        settings.load_module(__name__)

    from vigilo.common.logging import get_logger
    LOGGER = get_logger(__name__)

    if args:
        LOGGER.error(_('Too many arguments'))
        sys.exit(1)

    from vigilo.models.configure import configure_db
    try:
        configure_db(settings['database'], 'sqlalchemy_',
            settings['database']['db_basename'])
    except KeyError:
        LOGGER.error(_('No database configuration found'))
        sys.exit(1)

    from vigilo.models.session import DBSession
    from vigilo.models.tables import Event, CorrEvent, StateName, HLSHistory

    if options.days is None and options.size is None:
        parser.print_usage()
        sys.exit(1)

    if options.days is not None:
        if options.days > 0:
            # Génère une date qui se trouve options.days jours dans le passé.
            old_date = datetime.fromtimestamp(
                time.time() - options.days * 86400)

            # On supprime tous les événements dont l'idevent correspond à
            # un événement corrélé dont la dernière date d'activation est
            # plus vieille que old_date.
            # Comme les relations/FK sont créées en CASCADE, la suppression
            # des événements entraine aussi la suppression des événements
            # corrélés, des agrégats et de l'historique des événements.
            ids = DBSession.query(
                    Event.idevent
                ).join(
                    (CorrEvent, Event.idevent == CorrEvent.idcause)
                ).filter(StateName.statename.in_([u'OK', u'UP'])
                ).filter(CorrEvent.status == u'AAClosed'
                ).filter(CorrEvent.timestamp_active <= old_date).all()
            ids = [event.idevent for event in ids]
            nb_deleted = DBSession.query(Event).filter(
                            Event.idevent.in_(ids)).delete()
            LOGGER.info(_("Deleted %(nb_deleted)d closed events which were "
                            "at least %(days)d days old.") % {
                            'nb_deleted': nb_deleted,
                            'days': options.days,
                        })

            # On supprime les entrées d'historique concernant les changements
            # d'état des services de haut niveau qui ont été ajoutées avant
            # old_date.
            nb_deleted = DBSession.query(
                                HLSHistory
                            ).filter(HLSHistory.timestamp <= old_date
                            ).delete()
            LOGGER.info(_("Deleted %(nb_deleted)d entries in the history "
                        "for high level services which were at least "
                        "%(days)d days old.") % {
                            'nb_deleted': nb_deleted,
                            'days': options.days,
                        })

    if options.size is not None:
        if options.size > 0:
            # Calcule la taille actuelle de la base de données Vigilo.
            from sqlalchemy.engine.url import make_url
            url = make_url(settings['database']['sqlalchemy_url'])
            dbsize = DBSession.query(pg_database_size(url.database)).scalar()

            if dbsize > options.size:
                LOGGER.info(_("The database is %(size)d bytes big, which is "
                    "more than the limit (%(limit)d bytes). I will now delete "
                    "old closed events and history entries to make room for "
                    "new ones.") % {
                        'size': dbsize,
                        'limit': options.size,
                    })

            # On supprime les événements clos en commençant par
            # les plus anciens.
            total_deleted = 0
            while dbsize > options.size:
                idevent = DBSession.query(
                        Event.idevent
                    ).join(
                        (CorrEvent, Event.idevent == CorrEvent.idcause)
                    ).filter(StateName.statename.in_([u'OK', u'UP'])
                    ).filter(CorrEvent.status == u'AAClosed'
                    ).order_by(CorrEvent.timestamp_active.asc()).scalar()
                if idevent is None:
                    break

                nb_deleted = DBSession.query(Event).filter(
                                Event.idevent == idevent).delete()
                LOGGER.info(_("Deleted closed event #%d to make room for "
                                "new events.") % idevent)
                if not nb_deleted:
                    break
                total_deleted += nb_deleted

            # Affiche quelques statistiques.
            dbsize = DBSession.query(pg_database_size(url.database)).scalar()
            LOGGER.info(_("Deleted %(nb_deleted)d closed events. "
                "The database is now %(size)d bytes big (limit: "
                "%(limit)d bytes)") % {
                    'nb_deleted': total_deleted,
                    'size': dbsize,
                    'limit': options.size,
                })

            # On supprime les entrées d'historique concernant les changements
            # d'état des services de haut niveau, en commençant par les plus
            # anciens.
            total_deleted = 0
            while dbsize > options.size:
                idhistory = DBSession.query(HLSHistory.idhistory
                                ).order_by(HLSHistory.timestamp.asc()
                                ).scalar()
                if idhistory is None:
                    break

                nb_deleted = DBSession.query(HLSHistory).filter(
                                HLSHistory.idhistory == idhistory).delete()
                if not nb_deleted:
                    break
                total_deleted += nb_deleted

            # Affichage de statistiques actualisées.
            dbsize = DBSession.query(pg_database_size(url.database)).scalar()
            LOGGER.info(_("Deleted %(nb_deleted)d history entries on "
                        "high level services. The database is now %(size)d "
                        "bytes big (limit: %(limit)d bytes)") % {
                            'nb_deleted': total_deleted,
                            'size': dbsize,
                            'limit': options.size,
                        })

    transaction.commit()
    sys.exit(0)