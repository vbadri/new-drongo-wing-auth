# from ._activation_codes import ActivationCode
# from ._login_attempts import LoginAttempt
# from ._users import User
#
# import uuid
#
#
# class MysqlBackend(object):
#     def __init__(self, config):
#         self.config = config
#         self.users = User(self.config)
#         self.activation_codes = ActivationCode(self.config)
#         self.login_attempts = LoginAttempt(self.config)
#
#     def init(self):
#         self.users.init()
#         self.activation_codes.init()
#         self.login_attempts.init()
#
#     def check_user_exists(self, username):
#         return self.users.check_exists(username)
#
#     def create_user(self, username, password, active=False):
#         self.users.create(username, password, active)
