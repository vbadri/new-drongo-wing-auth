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


class Invitee(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'invite_code',
        'creator_id',
        'invitee_email_id',
        'expires',
        'last_updated'
        ]
    
    __resolve__ = {
        'creator': ('creator_id', User)
    }
    __autos__ = {
       'last_updated' : datetime.utcnow 
    }

    def set_expiry(self, span):
        self.expires = datetime.utcnow() + timedelta(minutes=span)
        self.save()