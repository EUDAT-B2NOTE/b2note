# various Flask API services not directly related to EVE framework
import google3_auth
from flask import Blueprint, jsonify

# web service endpoint provides user info
app  = Blueprint('b2note_api_services', __name__)

@app.route('/userinfo')
def index():
    if google3_auth.is_logged_in():
        user_info = google3_auth.get_user_info()
        return jsonify(user_info)
    return jsonify({"name":"Guest","status":"not logged in."})

