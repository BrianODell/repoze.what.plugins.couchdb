# -*- coding: utf-8 -*-
from repoze.who.plugins.basicauth import BasicAuthPlugin
from repoze.what.middleware import setup_auth
from repoze.what.plugins import couchdbkit

def AuthBasicMiddleware(app, global_config, **local_conf):

    if 'couchdb.uri' not in local_conf:
        local_conf['couchdb.uri'] = 'http://127.0.0.1:5984'

    server = couchdbkit.Server(local_conf['couchdb.uri'])
    db = server.get_or_create_db(local_conf['couchdb.db_name'])

    authenticator=couchdbkit.Authenticator(db)

    groups = couchdbkit.GroupAdapter(db)
    groups = {'all_groups': groups}

    basicauth = BasicAuthPlugin('Private web site')
    identifiers=[("basicauth", basicauth)]
    challengers=[("basicauth", basicauth)]

    authenticators=[("accounts", authenticator)]
    mdproviders=[("accounts", couchdbkit.MDPlugin(db))]

    permissions = {'all_perms': couchdbkit.PermissionAdapter(db)}

    return setup_auth(app,
                      groups,
                      permissions,
                      identifiers=identifiers,
                      authenticators=authenticators,
                      challengers=challengers,
                      mdproviders=mdproviders)

