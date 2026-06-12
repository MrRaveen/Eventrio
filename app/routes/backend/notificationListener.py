import os
import json
from flask import Blueprint, Response, session, stream_with_context
from app.config import getRedisClient

notification_bp = Blueprint('notification_listener', __name__)

@notification_bp.route('/listen', methods=['GET'])
def listen_notifications():
    """
    SSE endpoint — streams workflow completion notifications to the logged-in user.
    Subscribes to the NOTIFICATION_CHANNEL Redis pub/sub channel and only forwards
    messages whose userID matches the session user.
    """
    user_id = session.get('user_id', 'unknown_user')
    channel = os.getenv('NOTIFICATION_CHANNEL')

    def event_stream():
        redis_client = getRedisClient()
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(channel)
        print(f"[SSE] User '{user_id}' connected to notification stream on channel '{channel}'")

        try:
            for message in pubsub.listen():
                if message['type'] != 'message':
                    continue

                try:
                    raw = message['data']
                    if isinstance(raw, bytes):
                        raw = raw.decode('utf-8')

                    payload = json.loads(raw)

                    # Only forward messages that belong to this user
                    if payload.get('userID') != user_id:
                        continue

                    data = json.dumps(payload)
                    yield f"data: {data}\n\n"

                except (json.JSONDecodeError, Exception) as parse_err:
                    print(f"[SSE] Error parsing notification message: {parse_err}")
                    continue

        except GeneratorExit:
            print(f"[SSE] User '{user_id}' disconnected from notification stream")
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()

    return Response(
        stream_with_context(event_stream()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',       # Disable Nginx buffering
            'Connection': 'keep-alive',
        }
    )
