from ._common import MongoCollection

from datetime import datetime
from passlib.hash import pbkdf2_sha256

import uuid


class ActivationCode(MongoCollection):
    COLLECTION = 'auth_activation_codes'

    def create(self, user_uuid):
        code = uuid.uuid4().hex

        code_obj = {
            'user_uuid': user_uuid,
            'code': code,
            'created_on': datetime.utcnow()
        }
        self.collection.insert_one(user_obj)

    def verify(self, user_uuid, code):
        return self.collection.find(
            {'user_uuid': user_uuid, 'code': code}).count() > 0
