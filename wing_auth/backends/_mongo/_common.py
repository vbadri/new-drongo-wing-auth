class MongoCollection(object):
    def __init__(self, database):
        self.database = database

    def init(self):
        self.collection = self.database.instance.get_collection(
            self.COLLECTION)
