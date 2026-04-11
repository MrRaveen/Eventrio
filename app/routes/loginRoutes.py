import os

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, Flask, jsonify, redirect, render_template, session, url_for

from app.services.loginService import PerformLogin

auth_login = Blueprint('auth_login', __name__)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

oauth = OAuth()
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/documents https://www.googleapis.com/auth/drive.file'
    }
)

@auth_login.route('/login')
def login():
    return render_template('login.html')

@auth_login.route('/login/google')
def google_login():
    redirect_uri = url_for('auth_login.auth', _external=True)
    return google.authorize_redirect(redirect_uri, prompt='consent', access_type='offline')

@auth_login.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        session['user'] = user_info
        status = PerformLogin(user_data=user_info, token_data=token)
        if status:
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.pricing'))
    except Exception as e:
        return jsonify({"err":"error cooured","msg":str(e)})
         
@auth_login.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
