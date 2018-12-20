from datetime import datetime, timedelta

from wing_database.utils.mongo_orm.document import Document

class User(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'username',
        'password',
        'active',
        'superuser',
        'created_on',
        'last_updated'
    ]
    __autos__ = {
       'last_updated' : datetime.utcnow 
    }


class UserToken(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'user_id',
        'token',
        'expires',
        'last_updated'
    ]
    __autos__ = {
       'last_updated' : datetime.utcnow 
    }
    __resolve__ = {
        'user': ('user_id', User)
    }

    def refresh(self, span):
        self.expires = datetime.utcnow() + timedelta(minutes=span)
        self.save()

class Invite(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'email',
        'invite_code',
        'expires',
        'created_on',
        'last_updated'
    ]
    __autos__ = {
       'last_updated' : datetime.utcnow 
    }

    def refresh(self, span):
        self.expires = datetime.utcnow() + timedelta(minutes=span)
        self.save()