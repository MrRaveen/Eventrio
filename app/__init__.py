from app.models.organizations import Organizations
import os
import cloudinary
from bson import ObjectId
app_status = os.getenv('APP_STATUS')
if app_status == "Development":
    from app.inspector.execute import execute
    execute()
from flask import Flask
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_apscheduler import APScheduler
scheduler = APScheduler()
def create_app():
    cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Enable CORS for all routes - required for Google Meet add-on (cross-origin requests)
    CORS(app, origins="*", supports_credentials=False)

    scheduler.init_app(app)
    scheduler.start()

    import threading
    from app.orchestrator.saga.engine import background_orches_worker
    threading.Thread(target=background_orches_worker, daemon=True).start()
    @app.route('/test-push', methods=['GET'])
    def test_push():
        from app.config import getRedisClient
        redis_client = getRedisClient()
        channel = os.getenv('CHANNEL_NAME_ORCHESTRATOR')
        redis_client.publish(channel, '{"message": "simple"}')
        return {"status": "success", "message": f"Pushed to channel {channel}"}
    app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.config['SECRET_KEY'] = 'dev-secret-key'
    from app.db import init_db
    init_db()
    if app_status == "Development":
        userID = os.getenv('TEST_USER_ID')
        orgID = os.getenv('TEST_ORG_ID')
        foundOrg = Organizations.objects(id=orgID).first()
        if not foundOrg:
            #dummy org
            new_org = Organizations(
            id=ObjectId(f"{orgID}"),
            orgName="Global Event Planners LLC",
            address="456 Convention Center Blvd, Las Vegas, NV 89109",
            createdBy=f"{userID}",
            industry=["Sports"],
            userRole=["manager"]
            )
            new_org.save()  
    from app.routes.ui.loginRoutes import auth_login, oauth
    from app.routes.backend.paymentRoutes import payment
    from app.routes.ui.UIEndpoints import ui_endpoints
    from app.routes.backend.mainDashboard import main_dashboard
    from app.routes.backend.customerUi import customer_ui
    from app.routes.backend.eventUiRoutes import event_ui_routes
    from app.routes.ui.socialSetupRoutes import social_setups
    from app.routes.backend.notification import notification
    from app.routes.testing import testing_bp
    from app.routes.backend.notificationListener import notification_bp
    from app.routes.backend.AIRoutes import ai_routes_bp
    from errors import errors_bp
    from app.celery_init import init_celery

    oauth.init_app(app)
    app.register_blueprint(ui_endpoints)
    app.register_blueprint(auth_login)
    app.register_blueprint(payment,url_prefix='/payment')
    app.register_blueprint(main_dashboard,url_prefix='/main-dashboard')
    app.register_blueprint(customer_ui, url_prefix='/customer')
    app.register_blueprint(event_ui_routes,url_prefix="/event-ui")
    app.register_blueprint(social_setups)
    app.register_blueprint(notification)
    app.register_blueprint(testing_bp, url_prefix="/testing")
    app.register_blueprint(notification_bp, url_prefix="/notifications")
    app.register_blueprint(ai_routes_bp, url_prefix="/ai")
    app.register_blueprint(errors_bp)
    celery = init_celery(app)
    app.extensions["celery"] = celery
    return app
