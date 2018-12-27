import uuid

from datetime import datetime

from passlib.hash import pbkdf2_sha256

import pymongo

from .models import User, UserToken, Invitee, Device

HASHER = pbkdf2_sha256.using(rounds=10000)

class UserServiceBase(object):
    @classmethod
    def init(cls, module, users_collection='auth_users', tokens_collection='auth_user_tokens'):
        cls.module = module

        User.set_collection(
            module.database.instance.get_collection(users_collection)
        )
        User.__collection__.create_index([('username', pymongo.HASHED)])

        UserToken.set_collection(
            module.database.instance.get_collection(tokens_collection)
        )
        UserToken.__collection__.create_index([('token', pymongo.HASHED)])
        UserToken.__collection__.create_index([('expires', pymongo.ASCENDING)])

        Invitee.set_collection(
            module.database.instance.get_collection('auth_invites')
        )
        Invitee.__collection__.create_index([('invite_code', pymongo.HASHED)])
        Invitee.__collection__.create_index([('expires', pymongo.ASCENDING)])

        Device.set_collection(
            module.database.instance.get_collection('auth_devices')
        )
        Device.__collection__.create_index([('api_key', pymongo.HASHED)])


class UserForTokenService(UserServiceBase):
    def __init__(self, token):
        self.token = token

    def call(self):
        token = UserToken.objects.find_one(token=self.token)

        if token is None:
            return None

        if token.expires < datetime.utcnow():
            token.delete()
            return None

        token.refresh(span=self.module.config.token_age)
        return token.user


class UserCreateService(UserServiceBase):
    def __init__(self, username, password, active=False, superuser=False):
        self.username = username
        self.password = HASHER.hash(password)
        self.active = active
        self.superuser = superuser

    def check_exists(self):
        return User.objects.find_one(username=self.username) is not None

    def call(self, ctx=None):
        if self.check_exists():
            raise Exception('User already exists.')

        return User.create(
            username=self.username,
            password=self.password,
            active=self.active,
            superuser=self.superuser,
            created_on=datetime.utcnow()
        )


class UserChangePasswordService(UserServiceBase):
    def __init__(self, username, password):
        self.username = username
        self.password = HASHER.hash(password)

    def call(self):
        user = User.objects.find_one(username=self.username, active=True)
        user.password = self.password
        user.save()


class UserLoginService(UserServiceBase):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def check_credentials(self):
        user = User.objects.find_one(username=self.username, active=True)
        if user is None:
            return False

        return HASHER.verify(self.password, user.password)

    def create_token(self):
        user = User.objects.find_one(username=self.username, active=True)
        token = UserToken.create(
            user=user,
            token=uuid.uuid4().hex
        )
        token.refresh(span=self.module.config.token_age)
        return token.token

    def authenticate_session(self, ctx, token):
        sess = ctx.modules.session.get(ctx)
        sess.auth.token = token


class UserLogoutService(UserServiceBase):
    def expire_token(self, token):
        token = UserToken.objects.find_one(token=token)
        if token is not None:
            token.delete()

    def call(self, ctx):
        if 'session' in ctx.modules:
            sess = ctx.modules.session.get(ctx)
            sess.auth.token = None


class UserListService(UserServiceBase):
    def call(self, ctx):
        return User.objects.find()


class CreateInviteeService(UserServiceBase):
    def __init__(self, creator_id, email):
        self.creator = User.objects.find_one(_id=creator_id)
        self.invitee_email_id = email
    
    def call(self):
        if self.creator is None:
            return None

        invitee = Invitee.create(
            invite_code=uuid.uuid4().hex,
            creator_id=self.creator._id,
            invitee_email_id=self.invitee_email_id
        )
        invitee.set_expiry(span=self.module.config.invite_age)

        return invitee


# class InviteListService(UserServiceBase):
#     def call(self):
#         self.now = datetime.now()
#         convert ({expires: {"$lt": self.now}})
#         return Invitee.objects.find(expires<=self.now)


class InviteeForCodeService(UserServiceBase):
    def __init__(self, code):
        self.code = code

    def call(self):
        invitee = Invitee.objects.find_one(invite_code=self.code)

        if invitee is None:
            return None

        if invitee.expires < datetime.utcnow():
            return None

        return invitee


class DeviceForKeyService(UserServiceBase):
    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def call(self):
        device = Invitee.objects.find_one(api_key=self.key)

        if device is None:
            return None

        if device.api_secret != self.secret:
            return None

        return device
