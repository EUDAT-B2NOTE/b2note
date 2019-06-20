# implementation of google auth oauth2 client part for python / flask
# using authlib and loginpass

from flask import session, redirect
from authlib.flask.client import OAuth
# use loginpass to make OAuth connection simpler
from loginpass import create_flask_blueprint, Google
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
def convert(ui):
    myui = {'name':ui['name'],'given_name':ui['given_name'],'family_name':ui['family_name'],
            'provider':ui['iss'],'email':ui['email'],'id':ui['sub']}
    return myui

# store the token and user information as obtained from oauth
# in session only - no DB yet
def handle_authorize(remote, token, user_info):
    if token:
        print('handle_authorize remote name: token',remote.name,token)
        session[AUTH_TOKEN_KEY]=token['access_token']
        session[AUTH_REFRESH_TOKEN]=token['refresh_token']

        #save_token(remote.name, token)
    if user_info:
        print('handle_authorize userinfo',user_info)
        session[USER_INFO]=convert(user_info)
        #save_user(user_info)
        return redirect(BASE_URI,code=302)
    raise Exception('User not logged in.')


# register flask blueprint for google login logout and auth
# using authlib and loginpass

def register(app):
    oauth = OAuth(app)
    googlebp = create_flask_blueprint(Google, oauth, handle_authorize)
    app.register_blueprint(googlebp, url_prefix='/google')

    @app.route('/google/logout')
    def logout():
        session.pop(AUTH_TOKEN_KEY, None)
        session.pop(AUTH_REFRESH_TOKEN, None)
        session.pop(USER_INFO, None)
        return redirect(BASE_URI,code=302)
