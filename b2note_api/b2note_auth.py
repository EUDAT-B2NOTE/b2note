"""B2Note Api level authentication methods and integration with oauth providers

oauth providers provided by loginpass supported
Google provider explicitly added
B2Access provider implementation compatible with loginpass imported
"""
from eve.auth import TokenAuth
from flask import request,jsonify

# class implementing check_auth, it is used by Eve to verify during non-public operation (POST,PUT,DELETE,PATCH)
class B2NoteAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource, method):
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

def is_logged_in():
    """ function to return True or False based on whether current session is authenticatec """
    return True if AUTH_TOKEN_KEY in session else False

def get_user_info():
    """"function to return user information stored in current session"""
    ui = session[USER_INFO]
    ui['token']=session[AUTH_TOKEN_KEY]
    #print('get_user_info',ui['name'])
    return ui

def convertb2access(ui):
    """function to convert user information returned by b2access service

    returns this format:
    e.g.:{'name':'John Smith','id': '12345', 'email': 'js@example.com','provider':'b2access'}
    """
    myui = {'name':ui['name'],'id':ui['sub'],'email':ui['email'],'provider':'b2access'}
    return myui

def handle_authorize_b2access(remote, token, user_info):
    """handles the custom auth request for b2access, stores the token and user information as obtained from oauth
    in session and redirects to base_uri - usually b2note landing page http://localhost/b2note """
    if token:
        print('handle_authorize remote name: token',remote.name,token)
        session[AUTH_TOKEN_KEY]=token['access_token']
        session[AUTH_REFRESH_TOKEN]=token['refresh_token']

        #save_token(remote.name, token)
    if user_info:
        print('handle_authorize userinfo',user_info)
        #TODO consider storing user information in DB collection
        session[USER_INFO]=convertb2access(user_info)
        return redirect(BASE_URI,code=302)
    raise Exception('User not logged in.')

def convertgoogle(ui):
    """function to convert user information returned by google auth service in expected format:

    returns this format:
    e.g.:{'name':'John Smith','id': '12345', 'email': 'js@example.com','provider','google',...}
    """

    myui = {'name':ui['name'],'given_name':ui['given_name'],'family_name':ui['family_name'],
            'provider':ui['iss'],'email':ui['email'],'id':ui['sub']}
    return myui

def handle_authorize_google(remote, token, user_info):
    """ handles the custom auth request for google,

    stores the token and user information as obtained from oauth in current session structure
    """
    if token:
        print('handle_authorize remote name: token',remote.name,token)
        session[AUTH_TOKEN_KEY]=token['access_token']
        session[AUTH_REFRESH_TOKEN]=token['refresh_token']
    if user_info:
        print('handle_authorize userinfo',user_info)
        #TODO consider storing user information in DB collection
        session[USER_INFO]=convertgoogle(user_info)
        return redirect(BASE_URI,code=302)
    raise Exception('User not logged in.')


def register(app):
    """generates several flask blueprint for authentication (google,b2access) using authlib and loginpass


    registers these blueprints into Flask app instance
    and adds implementation of logout method + appropriate endpoint
    """
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

    # register flask endpoint for getting user information
    @app.route('/userinfo')
    def index():
        if is_logged_in():
            user_info = get_user_info()
            return jsonify(user_info)
        return jsonify({"name":"Guest","status":"not logged in."})