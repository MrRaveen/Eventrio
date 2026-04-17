from app.models.projects import Projects
from flask import (
    Blueprint,
    jsonify
)
event_ui_routes = Blueprint('event_ui_routes', __name__)
#get the media images
@event_ui_routes.route('/get-media/<string:eventID>', methods=['POST'])
def getMedia(eventID):
    try:
        if not eventID:
            return jsonify({
                "message": "error",
                "data": "Event ID is null"
            }), 404
        selectedEvent = Projects.objects(id=eventID).first()
        if not selectedEvent:
            return jsonify({
                "message": "error",
                "data": "Event is not found"
            }), 404
        allMediaLinks = selectedEvent.mediaLinks
        return allMediaLinks
    except Exception as e:
        return jsonify({
                "message": "error",
                "data": f"An error occurred: {str(e)}"
            }), 500






