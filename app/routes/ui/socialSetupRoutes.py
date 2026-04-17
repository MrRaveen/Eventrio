from app.models.userAcc import userAcc, socialMediaTokens
import os
import requests
from flask import Flask, request, redirect, session,Blueprint,url_for

social_setups = Blueprint('social_setups', __name__)

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FB_SECRET = os.environ.get('FACEBOOK_APP_SECRET')
REDIRECT_URI = os.environ.get('FACEBOOK_REDIRECT_URI')
@social_setups.route('/connect/meta')
def connectMeta():
    if not FB_APP_ID:
        return "Facebook App ID not configured.", 500
    scopes = "pages_show_list,pages_manage_posts,pages_read_engagement"
    state = session.get('user_id', '')
    auth_url = f"https://www.facebook.com/v19.0/dialog/oauth?client_id={FB_APP_ID}&redirect_uri={REDIRECT_URI}&scope={scopes}&state={state}"
    return redirect(auth_url)
@social_setups.route('/callbacks/meta')
def meta_callback():
    code = request.args.get('code')
    if not code:
        return "Authorization failed", 400

    #Exchange code for User Access Token
    token_url = f"https://graph.facebook.com/v19.0/oauth/access_token?client_id={FB_APP_ID}&redirect_uri={REDIRECT_URI}&client_secret={FB_SECRET}&code={code}"
    try:
        token_response = requests.get(token_url).json()
        user_access_token = token_response.get('access_token')
        if not user_access_token:
            return f"Failed to obtain user access token: {token_response.get('error', {}).get('message', 'Unknown error')}", 400

        #Exchange short-lived token for Long-Lived User Token (Valid for 60 days)
        long_lived_url = f"https://graph.facebook.com/v19.0/oauth/access_token?grant_type=fb_exchange_token&client_id={FB_APP_ID}&client_secret={FB_SECRET}&fb_exchange_token={user_access_token}"
        long_lived_response = requests.get(long_lived_url).json()
        long_lived_token = long_lived_response.get('access_token')
        if not long_lived_token:
            return f"Failed to obtain long-lived token: {long_lived_response.get('error', {}).get('message', 'Unknown error')}", 400
    except requests.exceptions.RequestException as e:
        return f"Request to Meta API failed: {str(e)}", 500

    state_user_id = request.args.get('state')
    user_id = session.get('user_id') or state_user_id
    if not user_id:
        return redirect(url_for('auth_login.login'))
    else:
        foundUser = userAcc.objects(sub=user_id).first()
        if not foundUser:
            return redirect(url_for('auth_login.login'))
        else:
            if not foundUser.socialMediaTokens:
                foundUser.socialMediaTokens = socialMediaTokens()
            foundUser.socialMediaTokens.facebook = long_lived_token
            foundUser.save()    
           
    return redirect(url_for('ui_endpoints.dashboard', tab='social_setup'))



