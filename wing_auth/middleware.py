import logging
logger = logging.getLogger('wing-auth-middleware')
class AuthMiddleware(object):
    def before(self, ctx):
        token = None
        if 'HTTP_AUTHORIZATION' in ctx.request.env:
            token = ctx.request.env['HTTP_AUTHORIZATION']

        elif 'session' in ctx.modules:
            try:
                sess = ctx.modules.session.get(ctx)
                token = sess.auth.get('token')
            except Exception:
                pass

        if token is not None:
            self.load_user_from_token(ctx, token)
            ctx.auth.invitee = None
        else:
            ctx.auth.user    = None

            invite_code = None
            logger.info("CTX env {}".format(ctx.request.env))
            if 'HTTP_INVITE_CODE' in ctx.request.env:
                code = ctx.request.env['HTTP_INVITE_CODE']
                logger.info("Got code {}".format(code))
                self.load_invitee_from_code(ctx, code)
                logger.info("Got invitee {}".format(ctx.auth.invitee))

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
