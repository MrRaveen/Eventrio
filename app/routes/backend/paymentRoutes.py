import os
import stripe
from dateutil.relativedelta import relativedelta
from flask import Blueprint, redirect, session, request, jsonify
from app.models.userAcc import userAcc, PaymentInfo
from datetime import datetime, timezone
from flask import Blueprint, redirect, session, request, jsonify, url_for
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
payment = Blueprint('payment', __name__)

@payment.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    user_id = session.get('user_id') 
    planName = request.form.get('planName')
    planAmount = request.form.get('planAmount') #in cents
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': planAmount, 
                    'product_data': {
                        'name': planName,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url= url_for('ui_endpoints.dashboard', _external=True), 
            cancel_url= request.host_url + 'pricing',    
            client_reference_id=user_id,
            metadata={
                'user_sub': user_id,
                'planName': planName
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 500

@payment.route('/webhook', methods=['POST'])
def webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
        
    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        metadata = session_data['metadata'] if 'metadata' in session_data else {}
        user_sub = metadata['user_sub'] if 'user_sub' in metadata else None
        planName = metadata['planName'] if 'planName' in metadata else ''
        
        if user_sub:
            user = userAcc.objects(sub=user_sub).first()
            if user:
                now = datetime.now(timezone.utc)
                db_tier = 'free'
                if planName and 'pro' in planName.lower():
                    db_tier = 'pro'
                elif planName and 'ultimate' in planName.lower():
                    db_tier = 'ultimate'

                user.accStatus = ['Active']
                user.payments = PaymentInfo(
                    tier=db_tier,
                    lastRenewedDate=now,
                    nextReniewDate=now + relativedelta(months=1) 
                )
                user.save()
                print(f"User {user_sub} activated successfully via Webhook with tier: {db_tier}.")
                
    return '', 200