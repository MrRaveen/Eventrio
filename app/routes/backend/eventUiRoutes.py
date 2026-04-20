from datetime import datetime
from app.models.tasks import TaskStatus
from app.models.tasks import TaskPriority
from app.models.tasks import tasks
from app.models.userAcc import userAcc
from app.responseDto.allColabPersonsDropdownRes import allColabPersonsDropdownRes
from app.models.enum.rolesEnum import rolesEnum
import os
from mongoengine.errors import ValidationError
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

#get the collaborators
@event_ui_routes.route('/get-collabs-dropdown/<string:eventID>', methods=['GET'])
def getCollabsDropdown(eventID):
    try:
        # Validation: Check if eventID is provided
        if not eventID or not eventID.strip():
            return jsonify({
                "message": "Validation Error",
                "data": "Event ID is required."
            }), 400

        # Query contributors for the specific event
        allCollabs = contributors.objects(eventID=eventID.strip())
        
        response_list = []

        for col in allCollabs:
            person_name = ""
            user_acc_id = col.userAccountID if col.userAccountID else ""
            status = "Accepted" if col.accept_stat else "Pending"

            # If accepted and account ID exists, fetch user details
            if col.accept_stat and col.userAccountID:
                user_info = userAcc.objects(sub=col.userAccountID).first()
                if user_info:
                    # Fallback to given/family name if displayName is not set
                    person_name = user_info.displayName or f"{user_info.givenName or ''} {user_info.familyName or ''}".strip()

            # Map data to the Pydantic response class
            collab_data = allColabPersonsDropdownRes(
                docID=str(col.id),
                userAccID=user_acc_id,
                personName=person_name,
                status=status,
                email=col.targetEmail
            )
            
            # Use .model_dump() for Pydantic V2 (use .dict() if on V1)
            response_list.append(collab_data.model_dump())

        return jsonify({
            "message": "Success",
            "data": response_list
        }), 200

    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500

#assign a user to task
@event_ui_routes.route('/assign-task/<string:docID>', methods=['PUT'])
def assignTask(docID):
    try:
        data = request.get_json()
        if not data or 'userID' not in data:
            return jsonify({
                "message": "Validation Error", 
                "data": "Missing 'userID' in JSON payload."
            }), 400
            
        user_id = data.get('userID')
        
        if not user_id or not str(user_id).strip():
            return jsonify({
                "message": "Validation Error", 
                "data": "'userID' cannot be empty."
            }), 400

        task = tasks.objects(id=docID.strip()).first()
        
        if not task:
            return jsonify({
                "message": "Not Found", 
                "data": "Task not found."
            }), 404

        # Cross-validation: Ensure target user is an accepted collaborator for this SPECIFIC event
        is_member = contributors.objects(eventID=task.event_id, userAccountID=user_id, accept_stat=True).first()
        if not is_member:
            return jsonify({
                "message": "Validation Error", 
                "data": "Target user is not an accepted collaborator for this project."
            }), 400

        task.assigned_to = str(user_id).strip()
        task.save()

        return jsonify({
            "message": "Success", 
            "data": "User assigned to task successfully."
        }), 200

    except ValidationError:
        return jsonify({
            "message": "Validation Error", 
            "data": "Invalid Document ID format."
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error", 
            "data": str(e)
        }), 500

#update tasks info
@event_ui_routes.route('/update-task/<string:docID>', methods=['PUT'])
def updateTask(docID):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "message": "Validation Error", 
                "data": "Missing JSON payload."
            }), 400

        task = tasks.objects(id=docID.strip()).first()
        
        if not task:
            return jsonify({
                "message": "Not Found", 
                "data": "Task not found."
            }), 404

        # Update title
        if 'title' in data:
            title = data.get('title')
            if not title or not str(title).strip():
                return jsonify({
                    "message": "Validation Error", 
                    "data": "Title is required and cannot be empty."
                }), 400
            task.title = str(title).strip()

        # Update description
        if 'description' in data:
            task.description = data.get('description')

        # Update priority
        if 'priority' in data:
            try:
                task.priority = TaskPriority(data.get('priority'))
            except ValueError:
                return jsonify({
                    "message": "Validation Error", 
                    "data": f"Invalid priority. Allowed values: {[e.value for e in TaskPriority]}"
                }), 400

        # Update status
        if 'status' in data:
            try:
                task.status = TaskStatus(data.get('status'))
            except ValueError:
                return jsonify({
                    "message": "Validation Error", 
                    "data": f"Invalid status. Allowed values: {[e.value for e in TaskStatus]}"
                }), 400

        # Update startDate
        if 'startDate' in data:
            start_date_str = data.get('startDate')
            if start_date_str:
                try:
                    # Supports ISO 8601 strings (e.g., "2026-05-01T09:00:00Z")
                    task.startDate = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        "message": "Validation Error", 
                        "data": "Invalid startDate format. Must be an ISO 8601 string."
                    }), 400
            else:
                task.startDate = None

        # Update deadline
        if 'deadline' in data:
            deadline_str = data.get('deadline')
            if deadline_str:
                try:
                    task.deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        "message": "Validation Error", 
                        "data": "Invalid deadline format. Must be an ISO 8601 string."
                    }), 400
            else:
                task.deadline = None

        task.save()

        return jsonify({
            "message": "Success", 
            "data": "Task details updated successfully."
        }), 200

    except ValidationError:
        return jsonify({
            "message": "Validation Error", 
            "data": "Invalid Document ID format."
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error", 
            "data": str(e)
        }), 500

#remove a task by doc ID
@event_ui_routes.route('/delete-task/<string:docID>', methods=['DELETE'])
def deleteTask(docID):
    try:
        # Validate docID presence
        if not docID or not docID.strip():
            return jsonify({
                "message": "Validation Error",
                "data": "Document ID is required."
            }), 400

        # Query the database for the task
        task = tasks.objects(id=docID.strip()).first()

        if not task:
            return jsonify({
                "message": "Not Found",
                "data": "Task not found or already deleted."
            }), 404

        # Perform the deletion
        task.delete()

        return jsonify({
            "message": "Success",
            "data": "Task deleted successfully."
        }), 200

    except ValidationError:
        # Triggers if docID is not a valid MongoDB ObjectId string
        return jsonify({
            "message": "Validation Error",
            "data": "Invalid Document ID format."
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500

#remove an assigned person
@event_ui_routes.route('/unassign-task/<string:docID>', methods=['PUT'])
def unassignTask(docID):
    try:
        # Validate docID presence
        if not docID or not docID.strip():
            return jsonify({
                "message": "Validation Error",
                "data": "Document ID is required."
            }), 400

        # Query the database for the task
        task = tasks.objects(id=docID.strip()).first()

        if not task:
            return jsonify({
                "message": "Not Found",
                "data": "Task not found."
            }), 404

        # Remove the assignment
        task.assigned_to = None
        task.save()

        return jsonify({
            "message": "Success",
            "data": "Task assignment removed successfully."
        }), 200

    except ValidationError:
        return jsonify({
            "message": "Validation Error",
            "data": "Invalid Document ID format."
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500        

#remove contributor
@event_ui_routes.route('/remove-contributor/<string:docID>', methods=['DELETE'])
def removeContributor(docID):
    try:
        # Validate docID presence
        if not docID or not docID.strip():
            return jsonify({
                "message": "Validation Error",
                "data": "Document ID is required."
            }), 400

        # Query the database for the contributor
        contributor = contributors.objects(id=docID.strip()).first()

        if not contributor:
            return jsonify({
                "message": "Not Found",
                "data": "Contributor not found."
            }), 404

        # Perform the deletion
        contributor.delete()

        return jsonify({
            "message": "Success",
            "data": "Contributor removed successfully."
        }), 200

    except ValidationError:
        return jsonify({
            "message": "Validation Error",
            "data": "Invalid Document ID format."
        }), 400
    except Exception as e:
        return jsonify({
            "message": "Internal Server Error",
            "data": str(e)
        }), 500

