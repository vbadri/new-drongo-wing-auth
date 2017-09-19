from wing_database.utils.mongo_orm.document import Document


class User(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'username',
        'password',
        'active',
        'superuser',
        'created_on'
    ]
