from eve.auth import BasicAuth
import os
from flask import request
from redis import StrictRedis,ConnectionPool


class B2NoteGauth(BasicAuth):
    def __init__(self):
        super(B2NoteGauth,self).__init__()
        self.redis=StrictRedis()
        self.redis.connection_pool = ConnectionPool.from_url(os.environ.get(
            'REDIS_URL','redis://localhost:6379'))

    def check_auth(self, token,  allowed_roles, resource, method):
        return token and self.redis.get(token);
        #return True
        #return username == 'test' and password == 'test'

    def authorized(self,allowed_roles,resource,method):
        try:
            token=request.headers.get('Authorization').split(' ')[1]
        except:
            token = None
        return self.check_auth(token,allowed_roles,resource,method)

if (os.getenv('GAUTH_CLIENT_ID')) is not None:
    google_oauth_client_id=os.environ['GAUTH_CLIENT_ID']
    google_oauth_client_secret=os.environ['GAUTH_CLIENT_SECRET']
