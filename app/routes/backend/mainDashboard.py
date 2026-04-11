from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from app.agents.agent_manager import agent_manager
from app.models.organizations import Organizations
from app.models.projects import Projects
from app.models.userAcc import userAcc

main_dashboard = Blueprint('main_dashboard', __name__)
@main_dashboard.route('/create-org', methods=['POST'])
def create_org():
    data = request.json
    try:
        user_info = session.get('user', {})
        user_sub = user_info.get('sub')
        new_org = Organizations(
            orgName=data.get('orgName', 'Unnamed Org'),
            address=data.get('address', ''),
            createdBy=user_sub,
            industry=[data.get('industry')],
            userRole=[data.get('userRole', 'manager')]
        )
        new_org.save()
        user_id = session.get('user_id')
        if user_id:
            user = userAcc.objects(sub=user_id).first()
            if user:
                user.limits.orgCount += 1
                user.save()
        return jsonify({"message": "Success", "id": str(new_org.id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@main_dashboard.route('/plan-event', methods=['POST'])
def chat_planning():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    if not agent_manager.planning_agent:
        return jsonify({"error": "Planning agent not initialized"}), 500
    try:
        user_id = session.get('user_id', 'unknown_user')
        response = agent_manager.run_agent(agent_manager.planning_agent, prompt, user_id)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main_dashboard.route('/plan-event/main', methods=['POST'])
def chat_main():
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({"error": "Prompt required"}), 400
    if not getattr(agent_manager, 'main_agent', None):
        return jsonify({"error": "Main agent not initialized"}), 500
    user_id = session.get('user_id', 'unknown_user')
    # Injecting system instructions manually
    enriched_prompt = f"[System: User executing this is '{user_id}'. You can use this ID for owner_id in tools] User Request: {prompt}"
    try:
        response = agent_manager.run_agent(agent_manager.main_agent, enriched_prompt, user_id)
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


