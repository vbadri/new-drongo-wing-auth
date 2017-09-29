from drongo.helpers import URLHelper

from wing_jinja2 import Jinja2


url = URLHelper.url
template = Jinja2.template


class AuthViews(object):
    def __init__(self, app, module, base_url):
        self.app = app
        self.module = module
        self.base_url = base_url

        URLHelper.mount(app, self, base_url)

    @url(pattern='/login')
    @template('auth/login.html.j2')
    def login_view(self, ctx):
        q = ctx.request.query
        if 'next' in q:
            ctx.session.next = q['next'][0]

    @url(pattern='/login', method='POST')
    def login_do(self, ctx):
        q = ctx.request.query
        username = q['username'][0]
        password = q['password'][0]

        svc = self.module.services.UserLoginService(
            username=username,
            password=password
        )

        result = svc.check_credentials()
        if result:
            svc.call(ctx)
            _next = None

            if 'next' in q:
                _next = q['next'][0]

            if _next is None and 'next' in ctx.session:
                _next = ctx.session.next

            if _next is None:
                _next = '/'

            ctx.response.set_redirect(_next)
        else:
            ctx.response.set_redirect('/auth/login')

    @url(pattern='/logout')
    def logout_do(self, ctx):
        q = ctx.request.query
        svc = self.module.services.UserLogoutService()
        svc.call(ctx)

        _next = q.get('next', ['/'])[0]
        ctx.response.set_redirect(_next)
