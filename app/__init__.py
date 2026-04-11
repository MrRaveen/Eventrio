from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    app.config['SECRET_KEY'] = 'dev-secret-key'
    from app.db import init_db
    init_db()
    from app.routes import mainRoutes
    from app.routes.loginRoutes import auth_login, oauth
    from app.routes.paymentRoutes import payment
    oauth.init_app(app)
    app.register_blueprint(mainRoutes.bp)
    app.register_blueprint(auth_login)
    app.register_blueprint(payment,url_prefix='/payment')
    return app
