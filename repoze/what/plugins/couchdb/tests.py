# -*- coding: utf-8 -*-
import unittest
from webtest import TestApp
from webob import Request, Response, exc
from repoze.what.plugins.couchdbkit.basic import AuthBasicMiddleware
from repoze.what.plugins import couchdbkit
from repoze.what.predicates import Any, is_user, has_permission, in_group


def application(environ, start_response):
    req = Request(environ)
    resp = Response()
    resp.content_type = 'text/plain'
    resp.body = 'anonymous'
    if req.path_info == '/secure':
        body = ''
        cred = environ.get('repoze.what.credentials', {})
        for k, v in cred.items():
            body += '%s: %s\n' % (k, v)
        for group in ('admin', 'others'):
            body += 'in_group(%r): %s\n' % (group, in_group(group).is_met(environ))
        for perm in ('read', 'write'):
            body += 'has_permision(%r): %s\n' % (perm, has_permission(perm).is_met(environ))
        resp.body = body
    return resp(environ, start_response)

class TestAuth(unittest.TestCase):

    db_name = 'repoze_what'

    def setUp(self):
        self.server = couchdbkit.Server()
        try:
            self.server.delete_db(self.db_name)
        except:
            pass
        db = self.server.get_or_create_db(self.db_name)
        couchdbkit.init_designs(db)

        couchdbkit.Permission.set_db(db)
        for name in ('read', 'write'):
            p = couchdbkit.Permission(name=name)
            p.save()

        couchdbkit.Group.set_db(db)
        for name in ('admin', 'users', 'others'):
            g = couchdbkit.Group(name=name)
            g.permissions = [p]
            g.save()

        couchdbkit.User.set_db(db)
        for name, pwd in (('Aladdin', 'open sesame'), ('User2', 'toto')):
            u = couchdbkit.User(username=name, password=pwd, active=True)
            u.encrypt_password()
            u.groups = [g]
            u.save()

        self.app = TestApp(AuthBasicMiddleware(application, {}, **{'couchdb.db_name': self.db_name}))

    def test_app(self):
        resp = self.app.get('/')
        resp.mustcontain('anonymous')

    def test_auth(self):
        resp = self.app.get('/secure', headers={'Authorization': 'Basic QWxhZGRpbjpvcGVuIHNlc2FtZQ=='})
        resp.mustcontain(
            "repoze.what.userid: ",
            "groups: ('others',)",
            "permissions: ('write',)",
            "in_group('admin'): False",
            "in_group('others'): True",
            "has_permision('read'): False",
            "has_permision('write'): True",
            )

    def test_auth_failure(self):
        resp = self.app.get('/secure', headers={'Authorization': 'Basic QWxhZGRpbjpvcGVuc2VzYW1l=='})
        resp.mustcontain(
            "in_group('admin'): False",
            "in_group('others'): False",
            "has_permision('read'): False",
            "has_permision('write'): False",
            )

