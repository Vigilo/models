# -*- coding: utf-8 -*-
"""
Script permettant de modifier le mot de passe
d'un utilisateur dans la base de données de Vigilo.
"""

import os
import pwd
import sys
import transaction
from optparse import OptionParser
import getpass

__all__ = (
    'change_password',
)

def change_password(*args):

    from vigilo.common.gettext import translate
    _ = translate(__name__)

    parser = OptionParser(
        usage=_("%prog [options] [username]"),
        description=_("Changes Vigilo's password for user 'username' "
            "or the currently logged in user if this argument is omitted."),
    )
    parser.add_option("-c", "--config", action="store", dest="config",
        type="string", default=None, help=_("Load configuration from "
        "this file."))
    parser

    (options, args) = parser.parse_args()

    from vigilo.common.conf import settings
    if options.config:
        settings.load_file(options.config)
    else:
        settings.load_module(__name__)

    from vigilo.common.logging import get_logger
    LOGGER = get_logger(__name__)

    if len(args) > 1:
        print _('Too many arguments')
        sys.exit(1)

    from vigilo.models.configure import configure_db
    try:
        configure_db(settings['database'], 'sqlalchemy_',
            settings['database']['db_basename'])
    except KeyError:
        print _('No database configuration found')
        sys.exit(1)

    from vigilo.models.session import DBSession
    from vigilo.models import tables

    current_password = None
    current_user = pwd.getpwuid(os.getuid())
    username = current_user.pw_name

    if len(args) > 0:
        username = args[0]

    msg = _("Changing Vigilo password for user '%s'.")
    LOGGER.info(msg, username)
    print msg % username

    # Si l'utilisateur n'est pas "root" (UID 0),
    # alors on demande le mot de passe actuel.
    if current_user.pw_uid != 0:
        current_password = getpass.getpass(_("Enter current password: "))

    user = tables.User.by_user_name(unicode(username))
    if user is None or (current_user.pw_uid != 0 and \
        not user.validate_password(current_password)):
        print _("Bad login or password.")
        sys.exit(1)

    new_password = getpass.getpass(_("Enter new password: "))
    new_password2 = getpass.getpass(_("Confirm new password: "))

    # Le nouveau mot de passe et sa
    # confirmation doivent coïncider.
    if new_password != new_password2:
        print _("Sorry, passwords do not match.")
        sys.exit(1)

    # Si le nouveau mot de passe est le même
    # que l'ancien, il n'y a rien à faire.
    if current_password == new_password:
        print _("Password unchanged.")
        sys.exit(0)

    user.password = new_password
    try:
        DBSession.flush()
        transaction.commit()
    except Exception:
        msg = _("An exception occurred while updating password for user '%s'.")
        LOGGER.exception(msg, username)
        print msg % username
        sys.exit(1)

    # Si on arrive ici, c'est que tout s'est bien passé.
    msg = _("Successfully updated password for user '%s'.")
    LOGGER.info(msg, username)
    print msg % username
    sys.exit(0)