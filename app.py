import requests
from flask import Flask, redirect, url_for, request, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token
from resources.user import UserLogin
from utils import jwt
from models import User, users  # Pastikan model User dan variabel users diimpor
from urllib.parse import urlencode

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-key'  # Kunci rahasia yang kuat
app.config['GOOGLE_CLIENT_ID'] = 'your_gclientid'
app.config['GOOGLE_CLIENT_SECRET'] = 'your_gclient_secret'
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

api = Api(app)
jwt.init_app(app)

api.add_resource(UserLogin, '/login')

def get_google_provider_cfg():
    return requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()

@app.route('/auth/google')
def google_login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    request_params = {
        "client_id": app.config['GOOGLE_CLIENT_ID'],
        "redirect_uri": url_for('google_callback', _external=True),
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    request_uri = f"{authorization_endpoint}?{urlencode(request_params)}"
    return redirect(request_uri)

@app.route('/auth/google/callback')
def google_callback():
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']

    code = request.args.get('code')
    token_url, headers, body = requests.Request(
        token_endpoint,
        code=code,
        redirect_uri=url_for('google_callback', _external=True),
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    ).prepare()

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config['GOOGLE_CLIENT_ID'], app.config['GOOGLE_CLIENT_SECRET']),
    )

    tokens = token_response.json()
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = requests.Request(
        userinfo_endpoint,
        access_token=tokens['access_token']
    ).prepare()

    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo = userinfo_response.json()

    if userinfo['email_verified']:
        unique_id = userinfo['sub']
        users_email = userinfo['email']
        picture = userinfo['picture']
        users_name = userinfo['given_name']

        # Simpan informasi pengguna di basis data atau buat pengguna baru
        user = User.find_by_username(users_email)
        if not user:
            user = User(id=unique_id, username=users_name, password="", email=users_email, picture=picture)
            users.append(user)

        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token)

    else:
        return "User email not available or not verified by Google.", 400

if __name__ == '__main__':
    app.run(debug=True)
