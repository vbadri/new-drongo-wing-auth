from drongo.helpers import URLHelper
from drongo.utils import dict2

from wing_jinja2 import Jinja2

from .backends.services import UserService


url = URLHelper.url
template = Jinja2.template


class AuthViews(object):
    def __init__(self, app, base_url, backend, session):
        self.app = app
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

    @url(pattern='/login')
    @template('auth/login.html.j2')
    def login_view(self, ctx):
        pass

    @url(pattern='/login', method='POST')
    def login_do(self, ctx):
        q = ctx.request.query
        username = q['username'][0]
        password = q['password'][0]

        result = self.services.user_service.login(
            ctx=ctx,
            username=username,
            password=password
        )

        if result:
            _next = q.get('next', ['/'])[0]
            ctx.response.set_redirect(_next)
        else:
            ctx.response.set_redirect('/auth/login')

    @url(pattern='/logout')
    def logout_do(self, ctx):
        q = ctx.request.query
        self.services.user_service.logout(
            ctx=ctx
        )
        _next = q.get('next', ['/'])[0]
        ctx.response.set_redirect(_next)
