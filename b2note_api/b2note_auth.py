# Api level authentication methods and integration with oauth providers
# oauth providers provided by loginpass supported
# Google provider explicitly added
# B2Access provider compatible with loginpass added

from eve.auth import TokenAuth
from flask import request,jsonify

# class implementing check_auth method in order to check whether session is logged - no other verification are made
class B2NoteAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
        #print('b2note auth:')
        #print(token,request.remote_addr,request.host)
        return is_logged_in() or (token=='test' and request.host=='localhost:5000')

# implementation of methods needed by b2note in order to get information from b2access oauth properties
# using authlib and loginpass to register b2access implementation of oauth
from flask import session, redirect
from authlib.flask.client import OAuth
from loginpass import create_flask_blueprint,Google
from loginpass_b2access import B2Access
import os

BASE_URI = os.environ.get("GAUTH_BASE_URI", default=False)
AUTH_TOKEN_KEY='auth_token'
AUTH_REFRESH_TOKEN='refresh_token'
USER_INFO='user_info'

#used by services to detect whether is logged
def is_logged_in():
    return True if AUTH_TOKEN_KEY in session else False

#return user info
def get_user_info():
    ui = session[USER_INFO]
    ui['token']=session[AUTH_TOKEN_KEY]
    print('get_user_info',ui['name'])
    return ui

# gets data from user_info structure returned by google oauth and converts to json
def convertb2access(ui):
    myui = {'name':ui['name'],'id':ui['sub'],'email':ui['email']}
    return myui

# store the token and user information as obtained from oauth
# in session only - no DB yet
def handle_authorize_b2access(remote, token, user_info):
    if token:
        print('handle_authorize remote name: token',remote.name,token)
        session[AUTH_TOKEN_KEY]=token['access_token']
        session[AUTH_REFRESH_TOKEN]=token['refresh_token']

        #save_token(remote.name, token)
    if user_info:
        print('handle_authorize userinfo',user_info)
        session[USER_INFO]=convertb2access(user_info)
        #save_user(user_info)
        return redirect(BASE_URI,code=302)
    raise Exception('User not logged in.')

# gets data from user_info structure returned by google oauth and converts to json
def convertgoogle(ui):
    myui = {'name':ui['name'],'given_name':ui['given_name'],'family_name':ui['family_name'],
            'provider':ui['iss'],'email':ui['email'],'id':ui['sub']}
    return myui

# store the token and user information as obtained from oauth
# in session only - no DB yet
def handle_authorize_google(remote, token, user_info):
    if token:
        print('handle_authorize remote name: token',remote.name,token)
        session[AUTH_TOKEN_KEY]=token['access_token']
        session[AUTH_REFRESH_TOKEN]=token['refresh_token']

        #save_token(remote.name, token)
    if user_info:
        print('handle_authorize userinfo',user_info)
        session[USER_INFO]=convertgoogle(user_info)
        #save_user(user_info)
        return redirect(BASE_URI,code=302)
    raise Exception('User not logged in.')


# register flask blueprint for google login logout and auth
# using authlib and loginpass
def register(app):
    oauth = OAuth(app)
    # registering flask blueprint with /b2access/login and /b2access/auth endpoints supporting oauth workflow
    b2accessbp = create_flask_blueprint(B2Access, oauth, handle_authorize_b2access)
    app.register_blueprint(b2accessbp, url_prefix='/b2access')

    # registering flask blueprint with /google/login and /google/auth endpoints supporting oauth workflow
    googlebp = create_flask_blueprint(Google, oauth, handle_authorize_google)
    app.register_blueprint(googlebp, url_prefix='/google')

    # registering flask endpoint to logout from any of the idp
    @app.route('/b2access/logout')
    @app.route('/google/logout')
    def logout():
        session.pop(AUTH_TOKEN_KEY, None)
        session.pop(AUTH_REFRESH_TOKEN, None)
        session.pop(USER_INFO, None)
        return redirect(BASE_URI,code=302)

    @app.route('/userinfo')
    def index():
        if is_logged_in():
            user_info = get_user_info()
            return jsonify(user_info)
        return jsonify({"name":"Guest","status":"not logged in."})
