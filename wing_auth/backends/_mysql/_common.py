class MySQLTable(object):
    def __init__(self, config):
        self.config = config

    def init(self):
        self.connection = self.config.modules.database.instance.get()
        # Try and create the schema
        try:
            cursor = self.connection.cursor()
            cursor.execute(self.SCHEMA)
            self.connection.commit()
        except Exception as _:
            pass
        finally:
            cursor.close()
