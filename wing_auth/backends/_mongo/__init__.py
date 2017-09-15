from ._activation_code import ActivationCode
from ._login_attempts import LoginAttempt
from ._users import User


class MongoBackend(object):
    def __init__(self, config):
        self.config = config
        self.modules = config.modules

        self.users = User(self.config)
        self.activation_codes = ActivationCode(self.config)
        self.login_attempts = LoginAttempt(self.config)

    def init(self):
        self.users.init()
        self.activation_codes.init()
        self.login_attempts.init()

    def check_user_exists(self, username):
        return self.users.check_exists(username)

    def create_user(self, username, password, active=False, superuser=False):
        self.users.create(username, password, active, superuser)

    def check_user_password(self, username, password):
        return self.users.check_password(username, password)

    def activate_user(self, username, code):
        pass

    def create_group(self, groupname, description=None):
        pass

    def delete_group(self, groupname):
        pass

    def add_user_to_group(self, groupname, username):
        pass

    def remove_user_from_group(self, groupname, username):
        pass

    def get_users_in_group(self, groupname):
        pass

    def get_groups_for_user(self, username):
        pass
