class MongoCollection(object):
    def __init__(self, config):
        self.config = config

    def init(self):
        self.collection = self.config.modules.database.instance.get_collection(
            self.COLLECTION)
