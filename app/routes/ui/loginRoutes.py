from app.models.userAcc import UserSpecificData
from app.models.userAcc import userAcc
from app.requestsDto.setupProfileReq import setupProfileReq
import os

from authlib.integrations.flask_client import OAuth
from flask import Blueprint,request, Flask, jsonify, redirect, render_template, session, url_for


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

@auth_login.route('/setup-profile', methods=['POST'])
def setup_profile():
    try:
        #get the req json
        reqData = request.get_json()
        if not reqData:
            return jsonify({
                "message":"Request data is empty",
                "data":"reqData"
            })
        #validate data    
        validated_data = setupProfileReq(**reqData)  
        userID = session.get('user_id')
        #update the profile part
        existing_user = userAcc.objects(sub=userID).first()
        if existing_user:
            existing_user.userSpecificData = UserSpecificData(
                industry = validated_data.industry,
                role = validated_data.role,
                averageAttendeeCount = validated_data.averageAttendeeCount,
                averageEventCountExcepected = validated_data.averageEventCountExcepected,
                toolStack = validated_data.toolStack,
                mainObjectiveOfUser = validated_data.mainObjectiveOfUser
            )
            existing_user.save()
            return jsonify({
                "status": "success",
                "redirect": url_for('ui_endpoints.dashboard')
            })
        else:
            return jsonify({
                "status": "error",
                "message": "User sequence not found in temporary storage."
            }), 500  
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"An unexpected error occurred: {str(e)}"
        }), 500


@auth_login.route('/auth')
def auth():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        user_sub = user_info.get('sub')
        session['user_id'] = user_sub
        existing_user = userAcc.objects(sub=user_sub).first()
        if existing_user:
            if token:
                existing_user.oauthToken = token
                existing_user.save()
                return redirect(url_for('ui_endpoints.dashboard'))
            else:
                return render_template('error.html', 
                    error_code='500', 
                    error_title='Token not found', 
                    error_message=f"The returned token from OAuth is null"
                ), 500 
        else:
            new_user = userAcc(
                sub=user_sub,
                email=user_info.get('email'),
                emailVerified=user_info.get('email_verified', False),
                displayName=user_info.get('name', ''),
                givenName=user_info.get('given_name', ''),
                familyName=user_info.get('family_name', ''),
                profilePicUrl=user_info.get('picture', ''),
                isOnline=True,
                accStatus = ['Pending-Payment'],
                oauthToken=token if token else {}
            )
            new_user.save()
            return redirect(url_for('ui_endpoints.pricing'))
         
    except Exception as e:
        return render_template('error.html', 
            error_code='500', 
            error_title='Error occured', 
            error_message=f"{str(e)}"
        ), 500
         
@auth_login.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
