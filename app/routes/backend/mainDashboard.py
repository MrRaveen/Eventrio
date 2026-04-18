from app.models.participants import Participants
from app.models.posts import Posts
from app.requestsDto.createOrgReq import createOrgReq
from pydantic import ValidationError
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from urllib.parse import urlparse
import cloudinary.uploader
import requests
from bson import ObjectId
from mongoengine import get_connection
from app.agents.agent_manager import agent_manager
from app.models.organizations import Organizations
from app.models.projects import Projects
from app.models.userAcc import userAcc

main_dashboard = Blueprint('main_dashboard', __name__)

#create organization
@main_dashboard.route('/create-org', methods=['POST'])
def create_org():
    data = request.json
    try:
        #get user ID
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "message": "error",
                "data": "User not logged in"
            }), 401
        #validate inserting json
        validatedJson = createOrgReq(**data)
        #create the org
        new_org = Organizations(
            orgName=validatedJson.orgName,
            address=validatedJson.address,
            createdBy=user_id,
            industry=[validatedJson.industry.value],
            userRole=[validatedJson.userRole.value]
        )
        new_org.save()
        user = userAcc.objects(sub=user_id).first()
        if user:
            user.limits.orgCount += 1
            user.save()  
        return jsonify({
                "message": "Success",
                "data": "Organization is created successfully"
            }), 201  
    except ValidationError as e:
        return jsonify({
                "message": "error",
                "data": f"Validation error: {str(e)}"
            }), 400
    except Exception as e:
        return jsonify({
                "message": "error",
                "data": f"An error occurred: {str(e)}"
            }), 500  

#update org
@main_dashboard.route('/update-org/<string:org_id>', methods=['PUT'])
def update_org(org_id):
    data = request.json
    try:
        #get user ID
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "message": "error",
                "data": "User not logged in"
            }), 401
        #validate inserting json
        validatedJson = createOrgReq(**data)
        #find the org and update
        org = Organizations.objects(id=org_id, createdBy=user_id).first()
        if not org:
            return jsonify({
                "message": "error",
                "data": "Organization not found or access denied"
            }), 404
        org.orgName = validatedJson.orgName
        org.address = validatedJson.address
        org.industry = [validatedJson.industry.value]
        org.userRole = [validatedJson.userRole.value]
        org.save()
        return jsonify({
                "message": "Success",
                "data": "Organization is updated successfully"
            }), 200  
    except ValidationError as e:
        return jsonify({
                "message": "error",
                "data": f"Validation error: {str(e)}"
            }), 400
    except Exception as e:
        return jsonify({
                "message": "error",
                "data": f"An error occurred: {str(e)}"
            }), 500  

#remove org
@main_dashboard.route('/remove-org/<string:org_id>', methods=["DELETE"])
def remove_org(org_id):
    mongo_client = get_connection()
    try:
        db_org_id = ObjectId(org_id)
    except Exception:
        return jsonify({
            "message": "error",
            "data": "Invalid organization ID format."
        }), 400

    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({
                "message": "error",
                "data": "User not logged in."
            }), 401

        foundUser = userAcc.objects(sub=user_id).first()
        if not foundUser:
            return jsonify({
                "message": "error",
                "data": "User not found."
            }), 404

        fbToken = None
        if hasattr(foundUser, 'socialMediaTokens') and foundUser.socialMediaTokens:
            fbToken = getattr(foundUser.socialMediaTokens, 'facebook', None)

        with mongo_client.start_session() as mongo_session:
            with mongo_session.start_transaction():
                # Check if organization exists and belongs to user
                org_query = {"_id": db_org_id, "createdBy": user_id}
                org_exists = Organizations._get_collection().find_one(org_query, session=mongo_session)
                if not org_exists:
                    return jsonify({
                        "message": "error",
                        "data": "Organization not found or access denied."
                    }), 404

                Organizations._get_collection().delete_one(org_query, session=mongo_session)

                #remove the media file safely
                foundProject = Projects.objects(orgID=org_id)
                for fo in foundProject:
                    if hasattr(fo, 'mediaLinks') and fo.mediaLinks:
                        for imgUrl in fo.mediaLinks:
                            try:
                                path = urlparse(imgUrl).path
                                if '/upload/' in path:
                                    parts = path.split('/upload/')[-1].split('/')
                                    if parts[0].startswith('v') and parts[0][1:].isdigit():
                                        parts.pop(0)    
                                    public_id_with_ext = '/'.join(parts)
                                    public_id = public_id_with_ext.rsplit('.', 1)[0]
                                    cloudinary.uploader.destroy(public_id)
                            except Exception as cloud_e:
                                print(f"Cloudinary deletion failed for {imgUrl}: {cloud_e}")

                    # Deleting slideshow (pptx)
                    if hasattr(fo, 'slideShowLink') and fo.slideShowLink:
                        try:
                            slideUrl = fo.slideShowLink
                            path = urlparse(slideUrl).path
                            if '/upload/' in path:
                                parts = path.split('/upload/')[-1].split('/')
                                if parts[0].startswith('v') and parts[0][1:].isdigit():
                                    parts.pop(0)
                                public_id_with_ext = '/'.join(parts)
                                public_id = public_id_with_ext.rsplit('.', 1)[0]
                                cloudinary.uploader.destroy(public_id, resource_type="raw")
                        except Exception as cloud_e:
                            print(f"Cloudinary deletion failed for slideshow {fo.slideShowLink}: {cloud_e}")
                                
                allPosts = Posts.objects(orgID=org_id)
                if fbToken:
                    for post in allPosts:
                        try:
                            if hasattr(post, 'postID') and post.postID:
                                delete_url = f"https://graph.facebook.com/v19.0/{post.postID}"
                                payload = {
                                    'access_token': fbToken
                                }
                                requests.delete(delete_url, params=payload, timeout=5)
                        except Exception as fb_e:
                            print(f"Facebook post deletion failed for {post.postID}: {fb_e}")

                Projects._get_collection().delete_many({"orgID": org_id}, session=mongo_session)
                Posts._get_collection().delete_many({"orgID": org_id}, session=mongo_session)
                Participants._get_collection().delete_many({"orgID": org_id}, session=mongo_session) 

        return jsonify({
            "message": "success",
            "data": "Organization and all related data removed successfully."
        }), 200
    except Exception as e:
        return jsonify({
                "message": "error",
                "data": f"Transaction failed or an error occurred: {str(e)}"
        }), 500

        
#get all the projects according to org ID
@main_dashboard.route('/get-org-projects/<string:org_id>')
def get_org_events(org_id):
    try:
        project_docs = Projects.objects(orgID=org_id)
        events = []
        for p in project_docs:
            events.append({
                "id": str(p.id),
                "name": p.name,
                "date": p.startDate.strftime('%Y-%m-%d') if p.startDate else "TBD",
                "status": "Started" if p.isEventStarted else "Upcoming"
            })
        return jsonify(events)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#main endpoint to plan the event
@main_dashboard.route('/plan-event/main', methods=['POST'])
def chat_main():
    data = request.json
    prompt = data.get('prompt')
    fbPageID = data.get('fbPageID')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    if not getattr(agent_manager, 'main_agent', None):
        return jsonify({"error": "Main agent not initialized"}), 500
    user_id = session.get('user_id', 'unknown_user')
    enriched_prompt = f"[System: User executing this is '{user_id}'. You can use this ID for owner_id in tools] User Request: {prompt}"
    try:
        response = agent_manager.run_agent(agent_manager.main_agent, prompt=enriched_prompt, fbPageID=fbPageID, user_id=user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_dashboard.route('/plan-event/create-media', methods=['POST'])
def trigger_media_agent():
    event_details = request.json.get('event_details')
    if not agent_manager.media_agent:
        return jsonify({"error": "Media agent not initialized"}), 500
    try:
        prompt = f"Create media for the following event: {event_details}"
        user_id = session.get('user_id', 'unknown_user')
        response = agent_manager.run_agent(agent_manager.media_agent, prompt, user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_dashboard.route('/plan-event/create-posts', methods=['POST'])
def trigger_social_agent():
    event_details = request.json.get('event_details')
    if not agent_manager.social_media_agent:
        return jsonify({"error": "Social media agent not initialized"}), 500

    try:
        prompt = f"Create social media posts for: {event_details}. Also, ask if these should be posted now or saved for later."
        user_id = session.get('user_id', 'unknown_user')
        response = agent_manager.run_agent(agent_manager.social_media_agent, prompt, user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_dashboard.route('/plan-event/stream', methods=['POST'])
def trigger_stream_agent():
    event_details = request.json.get('event_details')
    if not agent_manager.stream_handler_agent:
        return jsonify({"error": "Stream agent not initialized"}), 500

    try:
        prompt = f"Initialize stream and notify participants for: {event_details}."
        user_id = session.get('user_id', 'unknown_user')
        response = agent_manager.run_agent(agent_manager.stream_handler_agent, prompt, user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500        

# @main_dashboard.route('/plan-event', methods=['POST'])
# def chat_planning():
#     prompt = request.json.get('prompt')
#     if not prompt:
#         return jsonify({"error": "Prompt required"}), 400
#     if not agent_manager.planning_agent:
#         return jsonify({"error": "Planning agent not initialized"}), 500
#     try:
#         user_id = session.get('user_id', 'unknown_user')
#         response = agent_manager.run_agent(agent_manager.planning_agent, prompt, user_id)
#         return jsonify({"response": response})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#check social status
@main_dashboard.route('/social-status', methods=['GET'])
def social_status():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
        user = userAcc.objects(sub=user_id).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        tokens = user.socialMediaTokens
        status = {
            "facebook": bool(tokens and tokens.facebook and tokens.facebook != ""),
            "linkedIn": bool(tokens and tokens.linkedIn and tokens.linkedIn != ""),
            "youtube": bool(tokens and tokens.youtube and tokens.youtube != ""),
            "pinterest": bool(tokens and tokens.pinterest and tokens.pinterest != "")
        }
        return jsonify(status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#get the FB pages
@main_dashboard.route('/get-fb-pages', methods=['GET'])
def get_fb_pages():
    user_id = session.get('user_id')
    pages = []
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
       userData = userAcc.objects(sub=user_id).first()
       if userData and userData.socialMediaTokens and userData.socialMediaTokens.facebook:
            accounts_url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={userData.socialMediaTokens.facebook}"
            accounts_data = requests.get(accounts_url).json()
            for page in accounts_data.get('data', []):
                pages.append({
                    'page_id': page.get('id'),
                    'page_name': page.get('name')
                })
       return jsonify(pages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




