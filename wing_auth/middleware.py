class APIMiddleware(object):
    def before(self, ctx):
        if 'HTTP_AUTHORIZATION' in ctx.request.env:
            self.load_user_from_token(ctx)

    def load_user_from_token(self, ctx):
        token = ctx.request.env['HTTP_AUTHORIZATION']
        auth = ctx.modules.auth
        user_token_svc = auth.services.UserForTokenService(token=token)
        ctx.user = user_token_svc.call()
        print(ctx.user)
