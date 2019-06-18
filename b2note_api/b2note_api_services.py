# various Flask API services not directly related to EVE framework
import google_auth
from b2note_api import app
from flask import jsonify

# web service endpoint provides user info

@app.route('/userinfo')
def index():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        return jsonify(user_info)
    return jsonify({"status":"not logged in."})

