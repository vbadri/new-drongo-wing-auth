from drongo.helpers import URLHelper
from drongo.utils import dict2

from .backends.services import UserService

import json


url = URLHelper.url


class AuthAPI(object):
    def __init__(self, app, module, base_url, backend, session):
        self.app = app
        self.module = module
        self.base_url = base_url
        self.backend = backend
        self.session = session

        self.create_services()

        URLHelper.mount(app, self, base_url)

    def create_services(self):
        self.services = dict2()
        self.services.user_service = UserService(
            backend=self.backend,
            session=self.session
        )

    @url(pattern='/users/me')
    def users_me(self, ctx):
        sess = self.session.get(ctx)
        ctx.response.set_json({
            'status': 'OK',
            'payload': {
                'username': sess.user.username,
                'is_authenticated': sess.user.is_authenticated
            }
        })

    @url(pattern='/users', method='POST')
    def create_user(self, ctx):
        q = json.loads(ctx.request.env['BODY'])
        try:
            self.backend.create_user(
                username=q['username'],
                password=q['password'],
                active=self.module.active_on_register
            )
            ctx.response.set_json(dict(
                status='CREATED'
            ))
        except Exception:
            ctx.response.set_json(dict(
                status='ERROR',
                message='Could not create the user account.',
            ))

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
