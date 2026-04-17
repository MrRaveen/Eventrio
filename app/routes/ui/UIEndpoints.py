from typing import List
from app.responseDto.allEventsRes import ProjectSchema
from datetime import datetime, timezone
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

from app.models.enum.IndustryEnum import IndustryEnum
from app.models.enum.RoleEnum import RoleEnum
from app.models.enum.ObjectiveEnum import ObjectiveEnum
from app.models.enum.toolStackEnum import toolStackEnum

ui_endpoints = Blueprint('ui_endpoints', __name__)

@ui_endpoints.route('/')
def landing():
    return render_template('landing.html')

@ui_endpoints.route('/pricing')
def pricing():
    return render_template('pricing.html')

@ui_endpoints.route('/user-profile-ui',methods=['GET', 'POST'])
def user_profile_ui():
    try:
        industries = [e.value for e in IndustryEnum]
        roles = [e.value for e in RoleEnum]
        objectives = [e.value for e in ObjectiveEnum]
        tools = [e.value for e in toolStackEnum]
        return render_template('profile_setup.html', 
                             industries=industries, 
                             roles=roles, 
                             objectives=objectives, 
                             tools=tools)
    except Exception as e:
        return render_template('error.html', 
            error_code='404', 
            error_title='Page Not Found', 
            error_message="The URL you requested was not found on this server."
        ), 404

@ui_endpoints.route('/dashboard')
def dashboard():
    tab = request.args.get('tab', 'orgs')
    user_id = session.get('user_id')
    user = None
    try:
        if user_id:
            user = userAcc.objects(sub=user_id).first()
        
        org_docs = Organizations.objects(createdBy=user_id)
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
        print(f"Failed to fetch data: {e}")
    
    industries = [e.value for e in IndustryEnum]
    roles = [e.value for e in RoleEnum]
    return render_template('dashboard.html', 
                         active_tab=tab, 
                         orgs=orgs, 
                         user=user,
                         industries=industries, 
                         roles=roles)    

@ui_endpoints.route('/ai-planner')
def ai_planner():
    user_id = session.get('user_id')
    user = None
    try:
        if user_id:
            user = userAcc.objects(sub=user_id).first()
        
        org_docs = Organizations.objects(createdBy=user_id)
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
        print(f"Failed to fetch data: {e}")
    
    return render_template('ai_planner.html', 
                         active_tab='ai-planner', 
                         user=user,
                         orgs=orgs)

@ui_endpoints.route('/event-dashboard/<string:event_id>')
def event_dashboard(event_id):
    tab = request.args.get('tab', 'tasks')
    event = Projects.objects(id=event_id).first()
    if not event:
        return "Event not found", 404
    script_text = ""
    if event.scriptLink and event.scriptLink.startswith("data:text/plain"):
        raw_encoded = event.scriptLink.split(",", 1)[-1]
        script_text = unquote(raw_encoded)
    return render_template('event_dashboard.html', event=event, script_text=script_text, active_tab=tab)

@ui_endpoints.route('/browse-events')
def browse_events():
    now = datetime.now(timezone.utc)
    selected_id = request.args.get('selected')
    events = Projects.objects(startDate__gt=now, endDate__gt=now).order_by('startDate')
    
    allEventsResponse: List[ProjectSchema] = []
    for e in events:
        organization = Organizations.objects(id=e.orgID).first()
        org_name = organization.orgName if organization else "Unknown Organization"
        
        resObj = ProjectSchema(
            id = str(e.id),
            name = e.name,
            description = e.description,
            industry = e.industry,
            userRole = e.userRole,
            attendeeCountExpected = e.attendeeCountExpected,
            startDate = e.startDate,
            endDate = e.endDate,
            isEventStarted = e.isEventStarted,
            orgName = org_name,
            orgID = e.orgID,
            mediaLinks = e.mediaLinks,
            tasks = e.tasks
        )
        allEventsResponse.append(resObj)
        

    selected_event = None
    if selected_id:
        selected_event = next((e for e in allEventsResponse if e.id == selected_id), None)
    
    if not selected_event and allEventsResponse:
        selected_event = allEventsResponse[0]
        
    return render_template('browse_events.html', 
                         events=allEventsResponse, 
                         selected_event=selected_event)
