import sys
import traceback

from drongo.status_codes import HttpStatusCodes

from drongo_utils.endpoint import Endpoint


class AuthAPIEndpoint(Endpoint):
    __check__ = {}
    __filter__ = {}

    def do_rule(self, rtype, context, element=None):
        if hasattr(self, context):
            if element is None:
                context = getattr(self, context)()
            else:
                context = getattr(self, context)(element)
        else:
            context = {}

        rule = rtype(self)
        return rule.execute(context)

    def __call__(self):
        self.valid = True
        self.init()

        # Validate stage
        self.validate()
        if not self.valid:
            self.ctx.response.set_json({
                'status': 'ERROR',
                'errors': self.errors
            }, status=HttpStatusCodes.HTTP_400)
            return

        # Check stage
        self.authorize()
        if not self.authorized:
            self.ctx.response.set_json({
                'status': 'ERROR',
                'errors': self.errors
            }, status=HttpStatusCodes.HTTP_403)
            return

        # API Call
        try:
            result = self.call()

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            _logger = logging.getLogger('drongo')
            _logger.error('\n'.join(traceback.format_exception(
                exc_type, exc_value, exc_traceback)))

            self.error(message='Internal server error.')
            self.ctx.response.set_json({
                'status': 'ERROR',
                'errors': self.errors
            }, status=HttpStatusCodes.HTTP_500)
            return

        # Filter stage
        if isinstance(result, list):
            result = list(filter(
                lambda element: self.execute_filter(self.__filter__, element),
                result
            ))

        self.ctx.response.set_json({
            'status': 'OK',
            'payload': result
        })

    def init(self):
        pass

    def validate(self):
        pass

    def authorize(self):
        self.authorized = self.execute_auth(self.__check__)

    def execute_auth(self, expr):
        if '$and' in expr:
            for item in expr['$and']:
                res = self.execute_auth(item)
                if not res:
                    return False
            return True

        elif '$or' in expr:
            for item in expr['$or']:
                res = self.execute_auth(item)
                if res:
                    return True
            return False

        elif 'type' in expr:
            rtype = expr.get('type')
            ctx = expr.get('context')
            return self.do_rule(rtype, ctx)

        else:
            return True

    def execute_filter(self, expr, element):
        if '$and' in expr:
            for item in expr['$and']:
                res = self.execute_filter(item, element)
                if not res:
                    return False
            return True

        elif '$or' in expr:
            for item in expr['$or']:
                res = self.execute_filter(item, element)
                if res:
                    return True
            return False

        elif 'type' in expr:
            rtype = expr.get('type')
            ctx = expr.get('context')
            return self.do_rule(rtype, ctx, element)

        else:
            return True

    def error(self, group='_', message=''):
        self.errors.setdefault(group, []).append(message)
        self.valid = False
