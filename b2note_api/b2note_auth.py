from eve.auth import BasicAuth
import os

class MyBasicAuth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource,
                   method):
        return True
        #return username == 'test' and password == 'test'

google_oauth_client_id=os.environ['GAUTH_CLIENT_ID']
google_oauth_client_secret=os.environ['GAUTH_CLIENT_SECRET']
