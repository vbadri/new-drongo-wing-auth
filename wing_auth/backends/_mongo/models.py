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
        'creator',
        'expires',
        'last_updated'
        ]
    
    __resolve__ = {
        'creator': ('creator_id', User)
    }
    __autos__ = {
       'last_updated' : datetime.utcnow 
    }

class Invite(Document):
    __version__ = '1.0.0'
    __fields__ = [
        'email',
        'invite_code',
        'role',
        'org_id',
        'expires',
        'created_on',
        'last_updated'
    ]

    def refresh(self, span):
        self.expires = datetime.utcnow() + timedelta(minutes=span)
        self.save()


class UserOrgRole(Document):
    __fields__ = [
        'username',
        'organization_id',
        'role',
        'last_updated'
    ]
    __autos__ = {
        'last_updated': datetime.utcnow
    }
