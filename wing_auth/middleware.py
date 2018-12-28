class AuthMiddleware(object):
    def before(self, ctx):
        token = None

        ctx.auth.user    = None
        ctx.auth.invitee = None
        ctx.auth.auth_server = None

        if 'HTTP_AUTHORIZATION' in ctx.request.env:
            token = ctx.request.env['HTTP_AUTHORIZATION']

        elif 'session' in ctx.modules:
            try:
                sess = ctx.modules.session.get(ctx)
                token = sess.auth.get('token')
            except Exception:
                pass

        if token is not None:
            # This is a regular system user using a token derived
            # from their username and password. Load the user and
            # we are done
            self.load_user_from_token(ctx, token)
        else:
            if 'HTTP_API_KEY' in ctx.request.env:
                key = ctx.request.env['HTTP_API_KEY']
                secret = ctx.request.env['HTTP_API_SECRET'] or None
                self.load_server_from_credentials(ctx, key, secret)

            elif 'HTTP_INVITE_CODE' in ctx.request.env:
                code = ctx.request.env['HTTP_INVITE_CODE']
                self.load_invitee_from_code(ctx, code)


    def load_user_from_token(self, ctx, token):
        auth = ctx.modules.auth
        user_token_svc = auth.services.UserForTokenService(token=token)

        ctx.auth.token = token
        ctx.auth.user = user_token_svc.call()

    def load_invitee_from_code(self, ctx, code):
        auth = ctx.modules.auth
        invitee_code_svc = auth.services.InviteeForCodeService(code=code)

        ctx.auth.code = code
        ctx.auth.invitee = invitee_code_svc.call()

    def load_server_from_credentials(self, ctx, key, secret):
        auth = ctx.modules.auth
        auth_credentials_svc = auth.services.ServerFromCredentialsService(key=key, secret=secret)

        ctx.auth.api_key     = key
        ctx.auth.auth_server = auth_credentails_svc.call()
