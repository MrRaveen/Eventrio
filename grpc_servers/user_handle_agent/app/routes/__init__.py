from flask import Blueprint, jsonify

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello from user_handle_agent!"})
