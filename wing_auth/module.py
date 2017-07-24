from drongo.utils import dict2


class Auth(object):
    def __init__(self, app, **config):
        config = dict2.from_dict(config)
        self.app = app

        self.database_module = config.modules.database
        self.session_module = config.modules.session

        self.base_url = config.get('base_url', '/auth')
        self.api_base_url = config.get('api_base_url', '/api/auth')
        self.enable_api = config.get('enable_api', False)
        self.enable_views = config.get('enable_views', False)

        if config.get('backend') == 'mysql':
            from .backends._mysql import MysqlBackend
            self.backend = MysqlBackend(config)

        self.init()

    def init(self):
        self.backend.init()
        if self.enable_api:
            from .api import AuthAPI
            self.api = AuthAPI(
                app=self.app,
                base_url=self.api_base_url,
                backend=self.backend,
                session=self.session_module
            )
