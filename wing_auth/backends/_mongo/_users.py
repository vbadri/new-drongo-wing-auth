from ._common import MongoCollection

from datetime import datetime
from passlib.hash import pbkdf2_sha256

import uuid


class User(MongoCollection):
    COLLECTION = 'auth_users'

    def create(self, username, password, active=False):
        user_uuid = uuid.uuid4().hex
        password = pbkdf2_sha256.hash(password)

        user_obj = {
            'uuid': user_uuid,
            'username': username,
            'password': password,
            'is_active': active,
            'created_on': datetime.utcnow()
        }
        self.collection.insert_one(user_obj)

    def check_exists(self, username):
        return self.collection.find({'username': username}).count() > 0

    def verify_login(self, username, password):
        user_obj = self.collection.find_one(
            {'username': username, 'active': True})
        return pbkdf2_sha256.verify(password, user_obj['password'])

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
