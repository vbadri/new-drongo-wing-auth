import logging
logger = logging.getLogger('wing-auth-middleware')
class AuthMiddleware(object):
    def before(self, ctx):
        token = None

        ctx.auth.user    = None
        ctx.auth.invitee = None
        ctx.auth.auth_server = None
        ctx.auth.voice_assistant = None

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
            body = {}
            try:
                body = ctx.request.json
                if not isinstance(body, dict):
                    body = {}
            except:
                pass
                
            if 'api_key' in body:
                key    = body['api_key']
                secret = body['api_secret'] or None
                #logger.info("Key = {}, Secrete = {}".format(key, secret))
                self.load_server_from_credentials(ctx, key, secret)

            elif 'invite_code' in body:
                code = body['invite_code']
                logger.info("Got code {}".format(code))
                self.load_invitee_from_code(ctx, code)
                logger.info("Got invitee {}".format(ctx.auth.invitee))
				
			elif 'voice_assistant_token' in body:
				access_token = body['voice_assistant_token']
				self.load_assistant_from_token(ctx, access_token)		
				
            else:
                try:
                    x1 = ctx.request.env.keys() 
                except:
                    x1 = ctx.request.env
                logger.info(".....No valid credentials in body {}.....".format(ctx.request.env))


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
        ctx.auth.auth_server = auth_credentials_svc.call()

    def load_assistant_from_token(self, ctx, access_token):
        auth = ctx.modules.auth
        assistant_svc = auth.services.UserForAccessTokenService(access_token=access_token)
        ctx.auth.user, ctx.auth.voice_assistant = assistant_svc.call()
