from .models import User

from datetime import datetime
from passlib.hash import pbkdf2_sha256


HASHER = pbkdf2_sha256.using(rounds=10000)


class UserServiceBase(object):
    @classmethod
    def init(cls, module):
        cls.module = module
        User.set_collection(
            module.database.instance.get_collection('auth_users'))


class UserCreateService(UserServiceBase):
    def __init__(self, username, password, active=False, superuser=False):
        self.username = username
        self.password = HASHER.hash(password)
        self.active = active
        self.superuser = superuser

    def call(self, ctx=None):
        return User.create(
            username=self.username,
            password=self.password,
            active=self.active,
            superuser=self.superuser,
            created_on=datetime.utcnow()
        )


class UserLoginService(UserServiceBase):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_credentials(self):
        user = User.objects.find_one(username=self.username, active=True)
        if user is None:
            return False

        return HASHER.verify(self.password, user.password)

    def call(self, ctx):
        sess = ctx.modules.session.get(ctx)
        sess.user = {
            'is_authenticated': True,
            'username': self.username
        }


class UserLogoutService(UserServiceBase):
    def call(self, ctx):
        sess = ctx.modules.session.get(ctx)
        sess.user = {
            'is_authenticated': False,
            'username': None
        }
