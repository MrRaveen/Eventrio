import os
from app.requestsDto.reserveSeatReq import ParticipantSchema
from app.config import getRedisClient
from typing import List
import secrets
from app.models.participants import Participants
from app.models.projects import Projects
from datetime import datetime, timezone
from flask import (
    Blueprint,
    jsonify,
    request,
)
import resend

customer_ui = Blueprint('customer_ui', __name__)
redisReturnedClient = getRedisClient()
resend.api_key = os.getenv('RESEND_API_KEY')

@customer_ui.route('/get-verification-code/<string:email>')
def get_verification_code(email):
    """
    Generates a 6-digit verification code, stores it in Redis for 15 minutes,
    and sends it to the user's email via Resend.
    """
    code = str(secrets.randbelow(1000000)).zfill(6)
    redis_key = f"verify_email:{email}"
    
    # Store code (valid for 900 seconds / 15 minutes)
    if redisReturnedClient.set(name=redis_key, value=code, ex=900):
        try:
            params = {
                "from": "Eventrio <onboarding@resend.dev>",
                "to": [email],
                "subject": "Your Eventrio Verification Code",
                "html": f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #6366f1;">Eventrio Verification</h2>
                    <p>Your verification code is:</p>
                    <div style="font-size: 32px; font-weight: bold; color: #1e1b4b; letter-spacing: 4px; padding: 10px 0;">{code}</div>
                    <p style="color: #666;">This code will expire in 15 minutes.</p>
                </div>
                """
            }
            resend_resp = resend.Emails.send(params)
            return jsonify({
                "message": "Verification code sent successfully", 
                "data": resend_resp
            }), 200
        except Exception as e:
            return jsonify({
                "message": "Failed to send email. Please check your Resend configuration.",
                "error": str(e)
            }), 500
    
    return jsonify({"message": "Could not generate code, please try again."}), 400

@customer_ui.route('/verify-user', methods=['POST'])
def verify_user():
    """
    Verifies the code from Redis. If successful:
    1. Creates a participant record.
    2. Increments the event's attendee count.
    3. Sends a confirmation email.
    """
    try:
        data = request.get_json()
        validatedModel = ParticipantSchema(**data)
        
        redis_key = f"verify_email:{validatedModel.email}"
        stored_code = redisReturnedClient.get(redis_key)
        
        # 1. Verification Code Check
        if not stored_code:
            return jsonify({"message": "Verification code expired or not found"}), 400
            
        if validatedModel.verificationCode != stored_code:
            return jsonify({"message": "Invalid verification code"}), 400
            
        # 2. Event/Project Existence Check
        project = Projects.objects(id=validatedModel.eventID).first()
        if not project:
            return jsonify({"message": "Event not found"}), 404
            
        # 3. Duplicate Reservation Check
        existing_participant = Participants.objects(
            email=validatedModel.email, 
            eventID=validatedModel.eventID
        ).first()
        
        if existing_participant:
            return jsonify({"message": "You have already reserved a ticket for this event."}), 400
            
        # 4. Create Participant Record
        participant = Participants(
            name=validatedModel.name,
            email=validatedModel.email,
            eventID=validatedModel.eventID,
            orgID=validatedModel.orgID,
            isVerifiedStat=True,
            createdDate=datetime.now(timezone.utc)
        )
        participant.save()
        
        # 5. Atomically Decrement Attendee Count
        project.update(inc__attendeeCountExpected=-1)
        
        # 5. Clean up Redis
        redisReturnedClient.delete(redis_key)
        
        # 6. Send Confirmation Email
        try:
            conf_params = {
                "from": "Eventrio <onboarding@resend.dev>",
                "to": [validatedModel.email],
                "subject": f"Ticket Confirmed: {project.name}",
                "html": f"""
                <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                    <h2 style="color: #6366f1;">Reservation Confirmed!</h2>
                    <p>Hi <strong>{validatedModel.name}</strong>,</p>
                    <p>Your spot for <strong>{project.name}</strong> has been successfully reserved.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p><strong>Event Details:</strong></p>
                    <p>📅 Date: {project.startDate.strftime('%B %d, %Y')}</p>
                    <p>📍 Platform: Eventrio Online Portal</p>
                    <p style="font-size: 12px; color: #999; margin-top: 30px;">Thank you for using Eventrio!</p>
                </div>
                """
            }
            resend.Emails.send(conf_params)
        except Exception as email_err:
            # Log error but don't fail the verification since DB update succeeded
            print(f"Failed to send confirmation email: {email_err}")

        return jsonify({"message": "Successfully verified and reserved ticket"}), 200
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "An internal error occurred",
            "error": str(e)
        }), 500
