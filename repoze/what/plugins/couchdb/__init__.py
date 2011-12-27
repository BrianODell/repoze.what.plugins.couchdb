# -*- coding: utf-8 -*-
from zope.interface import implements
from repoze.who.interfaces import IAuthenticator
from repoze.who.interfaces import IMetadataProvider
from repoze.what.adapters import BaseSourceAdapter, SourceError
#from couchdbkit import Server, contain
#from couchdbkit.loaders import FileSystemDocsLoader
from couchdb import Server
from documents import Group, Permission, User
import os


class GroupAdapter(BaseSourceAdapter):
    """Group adapter. Use ``auth/group_users`` to retrieve group's users
    """

    def __init__(self, db):
        self.db = db

    def _get_all_sections(self):
        raise NotImplementedError()

    def _get_section_items(self, section):
        users = self.db.view('auth/group_users', key=section)
        return [doc['_id'] for doc in users]

    def _find_sections(self, hint):
        user = self.db.get(hint['repoze.what.userid'])
        groups = [doc['name'] for doc in user.get('groups', [])]
        return groups

    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        raise NotImplementedError()

    def _section_exists(self, section):
        raise NotImplementedError()

class PermissionAdapter(BaseSourceAdapter):
    """Permission adapter. Use view ``auth/group_by_name`` to retrieve allowed groups
    """

    def __init__(self, db):
        self.db = db

    def _get_all_sections(self):
        raise NotImplementedError()

    def _get_section_items(self, section):
        raise NotImplementedError()

    def _find_sections(self, hint):
        groups = self.db.view('auth/group_by_name', key=hint)
        for doc in groups:
            perms = doc.get('value', {}).get('permissions')
            perms = [doc['name'] for doc in perms]
            return perms
        return []

    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        raise NotImplementedError()

    def _section_exists(self, section):
        raise NotImplementedError()

class Authenticator(object):
    """Authenticator plugin. ``klass`` must be a ``couchdbkit.Document``.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.User`
    """
    implements(IAuthenticator)

    def __init__(self, db, klass=User):
        self.db = db
        self.klass = klass

    def authenticate(self, environ, identity):
        login = identity.get('login', '')
        password = identity.get('password', '')
        if login:
            user = self.klass.authenticate(self.db, login, password)
            if user is not None:
                identity['login'] = str(user.username)
                identity['user'] = user
                return user.id

class MDPlugin(object):
    """Metadata provider plugin. ``klass`` must be a ``couchdbkit.Document``.
    Default to :class:`~repoze.what.plugins.couchdbkit.documents.User`
    """
    implements(IMetadataProvider)

    def __init__(self, db, klass=User):
        self.db = db
        self.klass = klass

    def add_metadata(self, environ, identity):
        if 'user' not in identity:
            uid = identity['repoze.who.userid']
            if uid:
                user = self.klass.get(uid)
                identity['user'] = user

def init_designs(db):
    """Use ``couchdbkit.FileSystemDocsLoader`` to load design docs needed by plugins
    """
    design_docs = os.path.join(os.path.dirname(__file__), '_design')
    loader = FileSystemDocsLoader(design_docs)
    loader.sync(db, verbose=True)

