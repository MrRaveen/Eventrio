from flask import Blueprint, jsonify, request
from app.orchestrator.saga.engine import engine

testing_bp = Blueprint('testing', __name__)

@testing_bp.route('/start-engine', methods=['POST'])
def test_start_engine():
    try:
        data = request.json or {}
        # Use provided defaults if not in request
        user_id = data.get('userID', '104027687086786305179')
        org_id = data.get('orgID', '69f406b4eb4a9c318f5a954f')
        prompt = data.get('prompt', 'A test prompt for generating an awesome AI tech event in Colombo')
        page_id = data.get('page_id', None)

        # Start the engine asynchronously via celery
        engine.start_engine(userID=user_id, prompt=prompt, org_id=org_id, page_id=page_id)
        
        return jsonify({
            "status": "success", 
            "message": "SAGA engine started successfully. Check Celery logs.",
            "data_sent": {
                "userID": user_id,
                "orgID": org_id,
                "prompt": prompt,
                "page_id": page_id
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
