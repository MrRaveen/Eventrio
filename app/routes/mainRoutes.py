from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.models.organizations import Organizations
from app.models.projects import Projects
from app.models.userAcc import userAcc

bp = Blueprint('main', __name__)

@bp.route('/')
def landing():
    return render_template('landing.html')

@bp.route('/pricing')
def pricing():
    return render_template('pricing.html')

@bp.route('/dashboard')
def dashboard():
    tab = request.args.get('tab', 'orgs')
    try:
        # Fetch actual organizations
        org_docs = Organizations.objects()
        orgs = []
        for o in org_docs:
            orgs.append({
                "id": str(o.id),
                "orgName": o.orgName,
                "address": o.address,
                "industry": o.industry[0] if o.industry else "General",
                "userRole": o.userRole[0] if o.userRole else "member"
            })
    except Exception as e:
        orgs = []
        print(f"Failed to fetch orgs: {e}")

    return render_template('dashboard.html', active_tab=tab, orgs=orgs)

@bp.route('/api/org', methods=['POST'])
def create_org():
    data = request.json
    try:
        new_org = Organizations(
            orgName=data.get('orgName', 'Unnamed Org'),
            address=data.get('address', ''),
            industry=[data.get('industry', 'IT')],
            userRole=[data.get('userRole', 'manager')]
        )
        new_org.save()

        # Increment limit if needed
        user_id = session.get('user_id')
        if user_id:
            user = userAcc.objects(sub=user_id).first()
            if user:
                user.limits.orgCount += 1
                user.save()

        return jsonify({"message": "Success", "id": str(new_org.id)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/org/<string:org_id>/events')
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

from urllib.parse import unquote


@bp.route('/event/<string:event_id>')
def event_dashboard(event_id):
    """Event specific workspace showing tools."""
    event = Projects.objects(id=event_id).first()
    if not event:
        return "Event not found", 404

    script_text = ""
    if event.scriptLink and event.scriptLink.startswith("data:text/plain"):
        raw_encoded = event.scriptLink.split(",", 1)[-1]
        script_text = unquote(raw_encoded)

    return render_template('event_dashboard.html', event=event, script_text=script_text)

from app.agents.agent_manager import agent_manager


@bp.route('/api/chat/planning', methods=['POST'])
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

@bp.route('/api/chat/main', methods=['POST'])
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

@bp.route('/api/agent/media', methods=['POST'])
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

@bp.route('/api/agent/social', methods=['POST'])
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

@bp.route('/api/agent/stream', methods=['POST'])
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
