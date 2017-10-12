class Rule(object):
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def execute(self, context):
        return True

    def error(self, group='_', message=None):
        self.endpoint.error(group=group, message=message)
