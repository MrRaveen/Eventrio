from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from urllib.parse import unquote
from app.models.organizations import Organizations
from app.models.projects import Projects
from app.models.userAcc import userAcc

ui_endpoints = Blueprint('ui_endpoints', __name__)

@ui_endpoints.route('/')
def landing():
    return render_template('landing.html')

@ui_endpoints.route('/pricing')
def pricing():
    return render_template('pricing.html')

@ui_endpoints.route('/dashboard')
def dashboard():
    tab = request.args.get('tab', 'orgs')
    try:
        user_info = session.get('user', {})
        user_sub = user_info.get('sub')
        org_docs = Organizations.objects(createdBy=user_sub).first()
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

@ui_endpoints.route('/event-dashboard/<string:event_id>')
def event_dashboard(event_id):
    event = Projects.objects(id=event_id).first()
    if not event:
        return "Event not found", 404
    script_text = ""
    if event.scriptLink and event.scriptLink.startswith("data:text/plain"):
        raw_encoded = event.scriptLink.split(",", 1)[-1]
        script_text = unquote(raw_encoded)
    return render_template('event_dashboard.html', event=event, script_text=script_text)





