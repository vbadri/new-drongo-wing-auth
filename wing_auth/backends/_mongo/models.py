from datetime import datetime, timedelta

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

    def refresh(self, span):
        self.expires = datetime.utcnow() + timedelta(minutes=span)
        self.save()
