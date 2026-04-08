from app.models.users import users
from flask import session
def PerformLogin(user_data: dict, token_data: dict = None) -> bool:
    try:
        existing_user = users.objects(sub=user_data.get('sub')).first()
        user_sub = user_data.get('sub')
        if not user_sub:
            raise Exception("Err occured : user ID is null")
        session['user_id'] = user_sub
        if existing_user:
            if token_data:
                existing_user.oauthToken = token_data
                existing_user.save()
            return True
        else:
            new_user = users(
                id=user_data.get('sub'),
                sub=user_data.get('sub'),
                email=user_data.get('email'),
                emailVerified=user_data.get('email_verified', False),
                displayName=user_data.get('name', ''),
                givenName=user_data.get('given_name', ''),
                familyName=user_data.get('family_name', ''),
                profilePicUrl=user_data.get('picture', ''),
                oauthToken=token_data if token_data else {}
            )
            new_user.save()
            return False
            
    except Exception as e:
        raise Exception(f"Err occured : {str(e)}")