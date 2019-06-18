import functools
import json
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
import google_auth
from b2note_api import app
from flask import jsonify

@app.route('/userinfo')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        return jsonify(user_info)
    return jsonify({"status":"not logged in."})
