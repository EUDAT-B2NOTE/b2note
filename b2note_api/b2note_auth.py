# Api level authentication implementation
import google3_auth
from eve.auth import TokenAuth
from flask import request

class B2NoteAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        #print('b2note auth:')
        #print(token,request.remote_addr,request.host)

        return google3_auth.is_logged_in() or (token=='test' and request.host=='localhost:5000')
