import os
import stripe
import json
from bson import ObjectId
from bson.errors import InvalidId
from dateutil.relativedelta import relativedelta
from flask import Blueprint, redirect, session, request, jsonify, url_for, Response
from app.models.userAcc import userAcc, PaymentInfo
from datetime import datetime, timezone
from app.config import getRedisClient

notification = Blueprint('notification', __name__)

@notification.route('/stream', methods=['GET', 'POST'])
def stream():
    try:
        #redis channel subscription
        user_id = session.get('user_id')
        if not user_id:
            user_id = request.args.get('userID') or (request.json.get('userID') if request.is_json else None)
            
        if not user_id:
            return "Unauthorized", 401
            
        user = userAcc.objects(sub=user_id).first()
        if not user:
            try:
                user = userAcc.objects(id=ObjectId(user_id)).first()
            except (InvalidId, TypeError):
                pass
                
        if not user:
            return "Unauthorized", 401

        channel = f"user:{user.sub}"
        redis_client = getRedisClient()
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)
        
        #sse listenning
        def event_stream():
            try:
                for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')
                        yield f"data: {data}\n\n"
            except GeneratorExit:
                pubsub.unsubscribe(channel)
                pubsub.close()

        return Response(event_stream(), mimetype="text/event-stream")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@notification.route("/notify", methods=["POST"])
def notify():
    try:
        user_id = session.get('user_id')
        if not user_id:
            user_id = request.args.get('userID') or (request.json.get('userID') if request.is_json else None)
            
        if not user_id:
            return jsonify({"error": "userID required"}), 400
            
        user = userAcc.objects(sub=user_id).first()
        if not user:
            try:
                user = userAcc.objects(id=ObjectId(user_id)).first()
            except (InvalidId, TypeError):
                pass
                
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = request.get_json(force=True)
        redis_client = getRedisClient()
        redis_client.publish(f"user:{user.sub}", json.dumps(data))
        return {"status": "ok"}, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
