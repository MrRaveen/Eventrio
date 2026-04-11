from flask import session

from app.models.userAcc import userAcc


def PerformLogin(user_data: dict, token_data: dict = None) -> bool:
    try:
        user_sub = user_data.get('sub')
        if not user_sub:
            raise ValueError("User ID (sub) is missing from provider data.")

        session['user_id'] = user_sub
        existing_user = userAcc.objects(sub=user_sub).first()

        if existing_user:
            if token_data:
                existing_user.oauthToken = token_data
                existing_user.save()
            return True
        else:
            new_user = userAcc(
                sub=user_sub,
                email=user_data.get('email'),
                emailVerified=user_data.get('email_verified', False),
                displayName=user_data.get('name', ''),
                givenName=user_data.get('given_name', ''),
                familyName=user_data.get('family_name', ''),
                profilePicUrl=user_data.get('picture', ''),
                isOnline=True,
                accStatus = ['Pending-Payment'],
                oauthToken=token_data if token_data else {}
            )
            session['google_id'] = user_sub
            new_user.save()
            return False
    except Exception as e:
        print(f"Database save error details: {e}")
        raise Exception(f"Err occured : {str(e)}")
