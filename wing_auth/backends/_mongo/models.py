from wing_database.utils.mongo_orm.document import Document

from datetime import datetime, timedelta


class User(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'username',
        'password',
        'active',
        'superuser',
        'created_on'
    ]


class UserToken(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'user_id',
        'token',
        'expires'
    ]
    __resolve__ = {
        'user': ('user_id', User)
    }

    def refresh(self):
        self.expires = datetime.utcnow() + timedelta(minutes=5)
        self.save()
