from drongo.helpers import URLHelper
from drongo.utils import dict2
from drongo.utils import APIEndpoint

import json


url = URLHelper.url


class UserMe(APIEndpoint):
    __url__ = '/users/me'
    __http_methods__ = ['GET']

    def init(self):
        self.session = self.ctx.modules.session

    def call(self):
        sess = self.session.get(self.ctx)
        if 'user' in sess:
            return {
                'username': sess.user.username,
                'is_authenticated': sess.user.is_authenticated
            }
        else:
            return {
                'is_authenticated': False
            }


class UserCreate(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = ['POST']

    def init(self):
        self.query = dict2.from_dict(json.loads(self.ctx.request.env['BODY']))
        self.auth = self.ctx.modules.auth

    def validate(self):
        if 'username' not in self.query:
            self.errors.setdefault('username', []).append(
                'Username is required.'
            )
            self.valid = False

        if 'password' not in self.query:
            self.errors.setdefault('password', []).append(
                'Password is required.'
            )
            self.valid = False

    def call(self):
        self.auth.services.UserCreateService(
            username=self.query.username,
            password=self.query.password,
            active=self.auth.active_on_register
        ).call()

        return None


class UserLogin(APIEndpoint):
    __url__ = '/users/operations/login'
    __http_methods__ = ['POST']

    def init(self):
        self.query = dict2.from_dict(json.loads(self.ctx.request.env['BODY']))
        self.auth = self.ctx.modules.auth

    def validate(self):
        if 'username' not in self.query:
            self.errors.setdefault('username', []).append(
                'Username is required.'
            )
            self.valid = False

        if 'password' not in self.query:
            self.errors.setdefault('password', []).append(
                'Password is required.'
            )
            self.valid = False

        if not self.valid:
            return

        if not self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        ).check_credentials():
            self.valid = False
            self.errors.setdefault('_', []).append(
                'Invalid username or password.'
            )

            self.auth.services.UserLogoutService().call(self.ctx)

    def call(self):
        self.auth.services.UserLoginService(
            username=self.query.username,
            password=self.query.password
        ).call(self.ctx)


class UserLogout(APIEndpoint):
    __url__ = '/users/operations/logout'
    __http_methods__ = ['GET']

    def init(self):
        self.auth = self.ctx.modules.auth

    def call(self):
        self.auth.services.UserLogoutService().call(self.ctx)


class AuthAPI(object):
    def __init__(self, app, module, base_url):
        self.app = app
        self.module = module
        self.base_url = base_url

        self.init_endpoints()

    def init_endpoints(self):
        endpoints = [UserMe, UserCreate, UserLogin, UserLogout]

        for endpoint in endpoints:
            URLHelper.endpoint(
                app=self.app,
                klass=endpoint,
                base_url=self.base_url
            )
