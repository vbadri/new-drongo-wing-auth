from ._common import MongoCollection

from datetime import datetime
from passlib.hash import pbkdf2_sha256

import pymongo
import uuid


HASHER = pbkdf2_sha256.using(rounds=10000)


class User(MongoCollection):
    COLLECTION = 'auth_users'

    def init(self):
        super(User, self).init()

        self.collection.create_index('username', unique=True)
        self.collection.create_index([
            ('username', pymongo.HASHED),
        ])

    def create(self, username, password, active=False, superuser=False):
        password = HASHER.hash(password)

        user_obj = {
            'username': username,
            'password': password,
            'active': active,
            'superuser': superuser,
            'created_on': datetime.utcnow()
        }
        self.collection.insert_one(user_obj)

    def check_exists(self, username):
        return self.collection.find({'username': username}).count() > 0

    def check_password(self, username, password):
        user_obj = self.collection.find_one(
            {'username': username, 'active': True})
        if user_obj:
            return HASHER.verify(password, user_obj['password'])
        else:
            return False

    def activate(self, username):
        self.collection.update(
            {'username': username}, {'$set': {'active': True}})

    def deactivate(self, username):
        self.collection.update(
            {'username': username}, {'$set': {'active': False}})

    def change_password(self, username, new_password):
        password = pbkdf2_sha256.hash(new_password)
        self.collection.update(
            {'username': username}, {'$set': {'password': password}})
