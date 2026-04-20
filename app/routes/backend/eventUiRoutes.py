from app.models.enum.rolesEnum import rolesEnum
import os
from app.config import getMailjetClient
from app.models.contributors import contributors
from app.models.organizations import Organizations
from app.models.projects import Projects
from flask import (
    Blueprint,
    jsonify,
    request
)
event_ui_routes = Blueprint('event_ui_routes', __name__)

def generate_invitation_template(org_name, project_name, project_desc, app_url, target_email):
    """Generates the HTML email template for the invitation."""
    return f"""
    <div style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2>You have been invited to collaborate!</h2>
        <p><strong>{org_name}</strong> has invited you to join their project: <strong>{project_name}</strong>.</p>
        <p><strong>Project Details:</strong> {project_desc or 'No description provided.'}</p>
        <hr style="border: 1px solid #eee; margin: 20px 0;" />
        <h3>Action Required</h3>
        <p>To accept this invitation and access the project workspace, you must log in or create an account.</p>
        <p style="color: #d9534f; font-weight: bold;">
            Important: You must use this exact email address ({target_email}) to authenticate.
        </p>
        <p>
            <a href="{app_url}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px;">
                Go to Dashboard
            </a>
        </p>
    </div>
    """
#return the enums
@event_ui_routes.route('/get-roles', methods=['GET'])
def getRoles():
    try:
        roles_list = [role.value for role in rolesEnum]
        return jsonify({
            "message": "Success",
            "data": roles_list
        }), 200
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500

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
        return jsonify({
            "message": "success",
            "data": allMediaLinks
        }), 200
    except Exception as e:
        return jsonify({
                "message": "error",
                "data": f"An error occurred: {str(e)}"
            }), 500
#view contributors
@event_ui_routes.route('/view-contributors/<string:eventID>', methods=['GET'])
def viewContributors(eventID):
    try:
        # Validate eventID input
        if not eventID or not eventID.strip():
            return jsonify({
                "message": "Validation Error",
                "data": "Event ID cannot be empty."
            }), 400

        # Query contributors by eventID
        fetched_contributors = contributors.objects(eventID=eventID.strip())

        # Format the response data
        response_data = []
        for contributor in fetched_contributors:
            response_data.append({
                "id": str(contributor.id),
                "eventID": contributor.eventID,
                "orgID": contributor.orgID,
                "targetEmail": contributor.targetEmail,
                "accept_stat": contributor.accept_stat,
                "role": contributor.role,
                "userAccountID": contributor.userAccountID if contributor.userAccountID else "Pending Registration"
            })

        return jsonify({
            "message": "Success",
            "data": response_data
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500

#update role
@event_ui_routes.route('/update-contributor-role/<string:docID>', methods=['PUT'])
def updateContributorRole(docID):
    try:
        # Extract JSON payload
        data = request.get_json()
        
        if not data or 'roleName' not in data:
            return jsonify({
                "message": "Validation Error", 
                "data": "Missing required field: 'roleName' in JSON payload."
            }), 400

        role_name = data.get('roleName')

        # Validate against Enum
        try:
            valid_role = rolesEnum(role_name)
        except ValueError:
            return jsonify({
                "message": "Validation Error",
                "data": f"Invalid roleName. Allowed values are: {[e.value for e in rolesEnum]}"
            }), 400

        # Query contributor by document ID
        contributor = contributors.objects(id=docID).first()

        if not contributor:
            return jsonify({
                "message": "Not Found",
                "data": "Contributor not found for the provided Document ID."
            }), 404

        # Update and save the document
        contributor.role = valid_role.value
        contributor.save()

        return jsonify({
            "message": "Success",
            "data": "Contributor role updated successfully."
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500        

#send invitation
@event_ui_routes.route('/send-invitation', methods=['POST'])
def sendInvitation():
    try:
        # Extract JSON payload
        data = request.get_json()
        
        if not data:
            return jsonify({
                "message": "Validation Error", 
                "data": "Missing JSON payload."
            }), 400

        targetEmail = data.get('targetEmail')
        eventID = data.get('eventID')
        orgID = data.get('orgID')
        roleName = data.get('roleName')

        # Validate presence of required fields
        if not all([targetEmail, eventID, orgID, roleName]):
            return jsonify({
                "message": "Validation Error", 
                "data": "Missing required fields: targetEmail, eventID, orgID, and roleName are mandatory."
            }), 400

        # Validate Role Enum
        try:
            valid_role = rolesEnum(roleName)
        except ValueError:
            return jsonify({
                "message": "Validation Error",
                "data": f"Invalid roleName. Allowed values are: {[e.value for e in rolesEnum]}"
            }), 400

        # Validate Google Email
        if not targetEmail.lower().endswith('@gmail.com'):
            return jsonify({
                "message": "Validation Error",
                "data": "Only Google email addresses (@gmail.com) are permitted."
            }), 400

        # Validate Entities Existence
        getOrg = Organizations.objects(id=orgID).first()
        getProject = Projects.objects(id=eventID).first()

        if not getOrg or not getProject:
            return jsonify({
                "message": "Not Found",
                "data": "Invalid Organization or Project ID."
            }), 404

        # Check Duplication
        exists = contributors.objects(targetEmail=targetEmail, eventID=eventID).count() > 0
        if exists:
            return jsonify({
                "message": "Conflict",
                "data": "User has already been added to this project."
            }), 409

        # Save Contributor
        newContributor = contributors(
            eventID=eventID,
            orgID=orgID,
            targetEmail=targetEmail,
            role=valid_role.value
        )
        newContributor.save()

        # Prepare Email Payload
        app_home_url = os.getenv('APP_HOME_URL', 'http://localhost:5000')
        sender_email = os.getenv('MAILJET_SENDER_EMAIL')

        email_html = generate_invitation_template(
            org_name=getOrg.orgName,
            project_name=getProject.name,
            project_desc=getProject.description,
            app_url=app_home_url,
            target_email=targetEmail
        )

        mailjet = getMailjetClient()
        email_data = {
            "FromEmail": sender_email,
            "FromName": "Eventrio Invitation",
            "Subject": f"Invitation: Join {getProject.name} on Eventrio",
            "Html-part": email_html,
            "Recipients": [{"Email": targetEmail}]
        }

        # Send Email
        result = mailjet.send.create(data=email_data)

        if result.status_code != 200:
            newContributor.delete()
            error_details = "Unknown Mailjet error"
            try:
                error_details = result.json()
            except:
                error_details = result.text or error_details
            return jsonify({
                "message": "Email Delivery Failed",
                "data": error_details
            }), 502

        return jsonify({
            "message": "Success",
            "data": "Invitation sent successfully."
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500