# Api level authentication implementation
import google_auth
from eve.auth import BasicAuth
from flask import request

class B2NoteAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource, method):
        #print('auth:',username,password)
        return google_auth.is_logged_in() or (username=='test' and password=='test' and request.host=='localhost:5000')
        #return username == 'test' and password == 'test'
