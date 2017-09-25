from wing_database import Database
from wing_module import Module

import logging


class Auth(Module):
    """Drongo module for authentication and authorization"""

    __default_config__ = {
        'base_url': '/auth',
        'api_base_url': '/api/auth',

        'create_admin_user': True,
        'admin_user': 'admin',
        'admin_password': 'admin',

        'active_on_register': False,

        'enable_api': False,
        'enable_views': False,
    }

    logger = logging.getLogger('wing_auth')

    def init(self, config):
        self.logger.info('Initializing [auth] module.')

        self.app.context.modules.auth = self

        self.database = self.app.context.modules.database[config.database]

        if self.database.type == Database.MONGO:
            from .backends._mongo import services
            self.services = services

        else:
            raise NotImplementedError

        services.UserServiceBase.init(module=self)

        if config.create_admin_user:
            try:
                services.UserCreateService(
                    username=self.admin_user,
                    password=self.admin_password,
                    active=True,
                    superuser=True
                ).call()
            except Exception:
                pass

        self.init_api()
        self.init_views()

    def init_api(self):
        if not self.config.enable_api:
            return

        from .api import AuthAPI
        self.api = AuthAPI(
            app=self.app,
            module=self,
            base_url=self.config.api_base_url
        )

    def init_views(self):
        if not self.config.enable_views:
            return

        from .views import AuthViews
        self.views = AuthViews(
            app=self.app,
            module=self,
            base_url=self.config.base_url
        )
