from drongo.helpers import URLHelper


url = URLHelper.url


class AuthAPI(object):
    def __init__(self, app, base_url, backend, session):
        self.app = app
        self.base_url = base_url
        self.backend = backend
        self.session = session
        URLHelper.mount(app, self, base_url)

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
    def users_create(self, ctx):
        q = ctx.request.query
        self.backend.user_create(
            username=q['username'][0],
            password=q['password'][0],
            active=('active' in q)
        )
        ctx.response.set_json(dict(
            status='CREATED'
        ))

    @url(pattern='/users/operations/login', method='POST')
    def users_operations_login(self, ctx):
        q = ctx.request.query
        username = q['username'][0]
        password = q['password'][0]
        result = self.backend.login(
            ctx,
            username=username,
            password=password
        )

        if result:
            sess = self.session.get(ctx)
            sess.user.is_authenticated = True
            sess.user.username = username

            ctx.response.set_json(dict(
                status='OK',
                message='Logged in'
            ))
        else:
            ctx.response.set_json(dict(
                status='ERR',
                message='Invalid username or password.'
            ))

    @url(pattern='/users/operations/logout')
    def users_operations_logout(self, ctx):
        sess = self.session.get(ctx)
        sess.user.is_authenticated = False
        sess.user.username = 'anonymus'

        ctx.response.set_json(dict(
            status='OK',
            message='Logged out'
        ))
