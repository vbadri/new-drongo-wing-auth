from drongo.helpers import URLHelper
from drongo.utils import dict2
from drongo.utils import APIEndpoint

from .backends.services import UserService

import json


url = URLHelper.url


class UserMe(APIEndpoint):
    __url__ = '/users/me'
    __http_methods__ = ['GET']

    def prepare(self):
        self.session = self.ctx.modules.session

    def call(self):
        sess = self.session.get(self.ctx)
        return {
            'username': sess.user.username,
            'is_authenticated': sess.user.is_authenticated
        }


class UserCreate(APIEndpoint):
    __url__ = '/users'
    __http_methods__ = ['POST']

    def prepare(self):
        self.query = dict2.from_dict(json.loads(self.ctx.request.env['BODY']))
        self.modules = self.ctx.modules.auth

    def call(self):
        self.backend.create_user(
            username=self.query.username,
            password=self.query.password,
            active=self.module.active_on_register
        )
        self.ctx.response.set_json(dict(
            status='CREATED'
        ))


class UserLogin(APIEndpoint):
    __url__ = '/users/operation/login'
    __http_methods__ = ['POST']

    def prepare(self):
        self.query = dict2.from_dict(json.loads(self.ctx.request.env['BODY']))

    def call(self):
        pass


class AuthAPI(object):
    def __init__(self, app, module, base_url, backend, session):
        self.app = app
        self.module = module
        self.base_url = base_url
        self.backend = backend
        self.session = session

        self.create_services()

        URLHelper.mount(app, self, base_url)
        self.init_endpoints()

    def init_endpoints(self):
        endpoints = [UserMe, UserCreate]

        for endpoint in endpoints:
            URLHelper.endpoint(
                app=self.app,
                klass=endpoint,
                base_url=self.base_url
            )

    def create_services(self):
        self.services = dict2()
        self.services.user_service = UserService(
            backend=self.backend,
            session=self.session
        )

    @url(pattern='/users/operations/login', method='POST')
    def users_operations_login(self, ctx):
        q = json.loads(ctx.request.env['BODY'])
        username = q['username']
        password = q['password']

        result = self.services.user_service.login(
            ctx=ctx,
            username=username,
            password=password
        )

        if result:
            ctx.response.set_json(dict(
                status='OK',
                message='Logged in'
            ))
        else:
            ctx.response.set_json(dict(
                status='ERROR',
                message='Invalid username or password.'
            ))

    @url(pattern='/users/operations/logout')
    def users_operations_logout(self, ctx):
        self.services.user_service.logout(
            ctx=ctx
        )

        ctx.response.set_json(dict(
            status='OK',
            message='Logged out'
        ))
