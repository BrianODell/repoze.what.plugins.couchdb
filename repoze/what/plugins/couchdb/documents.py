# -*- coding: utf-8 -*-
#from couchdbkit import schema
#from couchdbkit import Document
from couchdb.mapping import TextField, BooleanField, ListField, Document
try:
    from hashlib import sha1
except:
    from sha import new as sha1

def encrypt_value(value):
    return sha1(value).hexdigest()

class Permission(Document):
    name = TextField()

class Group(Permission):
    permissions = ListField(TextField)

class User(Document):
    username = TextField()
    password = TextField()
    password_check = TextField(default='')
    groups = ListField(TextField)
    active = BooleanField()

    @classmethod
    def authenticate(cls, db, username, password):
        """Use view ``auth/user_by_name`` to check authentification.
        Return a :class:`~repoze.what.plugins.couchdbkit.documents.User` object on success.
        """
        results = cls.view(db, 'auth/user_by_name', key=username)
        for user in results.rows:
            if user and user.active and encrypt_value(password) == user.password:
                return user
            break

    def encrypt_password(self):
        """Encrypt password whith sha1 if not already done"""
        if self.password and self.password != self.password_check:
            self.password = encrypt_value(self.password)
            self.password_check = self.password

