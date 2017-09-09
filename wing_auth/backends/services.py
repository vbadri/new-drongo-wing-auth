class UserService(object):
    def __init__(self, backend, session):
        self._backend = backend
        self._session = session

    def login(self, ctx, username, password):
        res = self._backend.verify_credentials(
            username=username,
            password=password
        )
        if not res:
            return False

        sess = self._session.get(ctx)
        sess.user.is_authenticated = True
        sess.user.username = username
        return True

    def logout(self, ctx):
        sess = self._session.get(ctx)
        sess.user.is_authenticated = False
        sess.user.username = None
        return True

    def create(self, ctx, username, password, active=False, superuser=False):
        res = self._backend.check_user_exists(username)
        if res:
            return False, 'Username already exists!'

        self._backend.create_user(
            username=username,
            password=password,
            active=active,
            superuser=superuser
        )

        return True, None


class GroupService(object):
    pass
