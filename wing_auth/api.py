import json
import re

from drongo.status_codes import HttpStatusCodes
from drongo.utils import dict2

from drongo_utils.endpoint import APIEndpoint
from drongo_utils.helpers import URLHelper


url = URLHelper.url


class UsernameValidator(object):
    def __init__(self, api, username):
        self.api = api
        self.username = username

    def validate(self):
        if self.username is None or self.username == '':
            self.api.error(
                'username',
                'Username cannot be empty.'
            )
            return False

        m = re.match('[a-zA-Z][a-zA-Z0-9.]*', self.username)
        if (not m) or (m.group() != self.username):
            self.api.error(
                'username',
                'Only alpha number characters and underscore is allowed.'
            )
            return False

        return True


class PasswordValidator(object):
    def __init__(self, api, password):
        self.api = api
        self.password = password

    def validate(self):
        if self.password is None or self.password == '':
            self.api.error(
                'password',
                'Password cannot be empty.'
            )
            return False

        if len(self.password) < 5:
            self.api.error(
                'password',
                'Password must be at least 5 characters.'
            )
            return False
        return True


class UserMe(APIEndpoint):
    __url__ = '/users/me'
    __http_methods__ = ['GET']

    def init(self):
        self.token = self.ctx.auth.get('token')
        self.auth = self.ctx.modules.auth
        self.user_token_svc = self.auth.services.UserForTokenService(
            token=self.token
        )

    def validate(self):
        if self.token is None:
            self.valid = False
            self.error(message='No auth token specified.')
            return

        self.user = self.user_token_svc.call()
        if self.user is None:
            self.valid = False
            self.errors.setdefault('_', []).append(
                'Invalid or unauthorized token.'
            )

    def call(self):
        return {
            'username': self.user.username,
            'is_authenticated': True,
            'is_superuser': self.user.superuser
        }


class UserCreate(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = ['POST']

    def init(self):
        self.query = self.ctx.request.json
        self.auth = self.ctx.modules.auth
        self.create_user_svc = self.auth.services.UserCreateService(
            username=self.query.get('username'),
            password=self.query.get('password'),
            active=self.auth.config.active_on_register
        )

    def validate(self):
        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('password')).validate()
        )

        if self.create_user_svc.check_exists():
            self.error(
                group='username',
                message='Username already exists.'
            )
            self.valid = False

    def call(self):
        self.create_user_svc.call()
        return 'OK'


class UserChangePassword(APIEndpoint):
    __url__ = '/users/operations/change-password'
    __http_methods__ = ['POST']

    def init(self):
        self.query = self.ctx.request.json
        self.auth = self.ctx.modules.auth

        self.login_svc = self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        )

        self.change_pwd_svc = self.auth.services.UserChangePasswordService(
            username=self.query.username,
            password=self.query.new_password
        )

    def validate(self):
        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('password')).validate()
        )

        if not self.login_svc.check_credentials():
            self.error(
                group='_',
                message='Invalid username or password.'
            )

    def call(self):
        self.change_pwd_svc.call()
        return 'OK'


class UserLogin(APIEndpoint):
    __url__ = '/users/operations/login'
    __http_methods__ = ['POST']

    def init(self):
        self.query = dict2.from_dict(json.loads(self.ctx.request.env['BODY']))
        self.auth = self.ctx.modules.auth

        self.login_svc = self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        )

    def validate(self):
        self.valid = (
            self.valid and
            UsernameValidator(self, self.query.get('username')).validate()
        )

        self.valid = (
            self.valid and
            PasswordValidator(self, self.query.get('password')).validate()
        )

        if not self.valid:
            return

        if not self.login_svc.check_credentials():
            self.valid = False
            self.error(message='Invalid username or password.')
            self.auth.services.UserLogoutService().call(self.ctx)

    def call(self):
        token = self.login_svc.create_token()

        if self.auth.config.token_in_session:
            self.login_svc.authenticate_session(self.ctx, token)

        self.status(HttpStatusCodes.HTTP_202)

        return {
            'token': token
        }


class UserLogout(APIEndpoint):
    __url__ = '/users/operations/logout'
    __http_methods__ = ['GET']

    def init(self):
        self.auth = self.ctx.modules.auth
        self.token = self.ctx.auth.get('token')

    def call(self):
        self.auth.services.UserLogoutService().expire_token(self.token)
        self.status(HttpStatusCodes.HTTP_202)
        return 'Bye!'


class UserList(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = 'GET'

    def init(self):
        self.auth = self.ctx.modules.auth
        self.user = self.ctx.auth.user

    def validate(self):
        if not self.user or not self.user.superuser:
            self.error(
                group='_',
                message='Only superuser is allowed to list the users.'
            )

    def call(self):
        return list(map(
            lambda item: item.json(exclude=['password', '_id', 'created_on']),
            self.auth.services.UserListService().call(self.ctx)
        ))


AVAILABLE_API = [
    UserMe,
    UserCreate,
    UserLogin,
    UserLogout,
    UserChangePassword,
    UserList
]


class AuthAPI(object):
    def __init__(self, app, module, base_url):
        self.app = app
        self.module = module
        self.base_url = base_url

        self.init_endpoints()

    def init_endpoints(self):
        for endpoint in AVAILABLE_API:
            URLHelper.endpoint(
                app=self.app,
                klass=endpoint,
                base_url=self.base_url
            )
