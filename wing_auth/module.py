from wing_database import Database
from wing_module import Module

from drongo.utils import dict2


class Auth(Module):
    def init(self, config):
        self.modules = config.modules

        self.base_url = config.get('base_url', '/auth')
        self.api_base_url = config.get('api_base_url', '/api/auth')

        self.enable_api = config.get('enable_api', False)
        self.enable_views = config.get('enable_views', False)

        self.active_on_register = config.get('active_on_register', False)
        database = self.modules.database

        if database.type == Database.MONGO:
            from .backends._mongo import MongoBackend
            self.backend = MongoBackend(config)

        else:
            raise NotImplementedError

        self.backend.init()

        if self.enable_api:
            from .api import AuthAPI
            self.api = AuthAPI(
                app=self.app,
                module=self,
                base_url=self.api_base_url,
                backend=self.backend,
                session=self.modules.session
            )

        if not self.backend.check_user_exists('admin'):
            self.backend.create_user(
                username='admin',
                password='admin',
                active=True,
                superuser=True
            )
