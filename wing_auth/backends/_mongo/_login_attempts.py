from ._common import MongoCollection

from datetime import datetime
from passlib.hash import pbkdf2_sha256

import uuid


class LoginAttempt(MongoCollection):
    COLLECTION = 'auth_login_attempts'

    def add(self, user_uuid, session_id, status):
        user_uuid = uuid.uuid4().hex
        password = pbkdf2_sha256.hash(password)

        user_obj = {
            'user_uuid': user_uuid,
            'session_id': session_id,
            'status': status,
            'attempted_on': datetime.utcnow()
        }
        self.collection.insert_one(user_obj)

    def get_for_user(self, user_uuid):
        return self.collection.find({'user_uuid': user_uuid})
