import logging
from flask import Blueprint, jsonify
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from flask_limiter.errors import RateLimitExceeded


logger = logging.getLogger(__name__)
errors_bp = Blueprint('errors', __name__)

class APIError(Exception):
    def __init__(self, error_code: str, error_message: str):
        super().__init__()
        self.error_code = error_code
        self.error_message = error_message

@errors_bp.app_errorhandler(APIError)
def handle_api_error(error):
    response = {
        "error_code": error.error_code,
        "message": error.error_message
    }
    logger.error(f"APIError: {error.error_message}")
    return jsonify(response), 400

@errors_bp.app_errorhandler(RateLimitExceeded)
def handle_rate_limit_exceeded(error):
    response = {
        "error_code": "RATE_LIMIT_EXCEEDED",
        "message": getattr(error, 'error_message', str(error))
    }
    logger.warning(f"RateLimitExceeded: {str(error)}")
    return jsonify(response), 429

@errors_bp.app_errorhandler(NotFound)
def handle_not_found_error(error):
    response = {
        "error_code": "NOT_FOUND",
        "message": error.description if hasattr(error, 'description') else str(error)
    }
    logger.error(f"NotFound: {str(error)}")
    return jsonify(response), 404

@errors_bp.app_errorhandler(MethodNotAllowed)
def handle_method_not_allowed_error(error):
    response = {
        "error_code": "METHOD_NOT_ALLOWED",
        "message": error.description if hasattr(error, 'description') else str(error)
    }
    logger.error(f"MethodNotAllowed: {str(error)}")
    return jsonify(response), 405

@errors_bp.app_errorhandler(BadRequest)
def handle_bad_request_error(error):
    response = {
        "error_code": "BAD_REQUEST",
        "message": error.description if hasattr(error, 'description') else str(error)
    }
    logger.error(f"BadRequest: {str(error)}")
    return jsonify(response), 400
