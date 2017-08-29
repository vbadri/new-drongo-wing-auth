from ._activation_code import ActivationCode
from ._users import User

import uuid


class MongoBackend(object):
    def __init__(self, config):
        self.config = config
        self.users = User(self.config)
        self.activation_codes = ActivationCode(self.config)

    def init(self):
        self.users.init()
        self.activation_codes.init()

    def check_user_exists(self, username):
        return self.users.check_exists(username)

    def create_user(self, username, password, active=False):
        self.users.create(username, password, active)
