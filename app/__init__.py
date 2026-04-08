from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'

    from app.db import init_db
    init_db()

    from app.routes import mainRoutes
    from app.routes.loginRoutes import oauth
    from app.routes.loginRoutes import auth_login
    oauth.init_app(app)
    app.register_blueprint(mainRoutes.bp)
    app.register_blueprint(auth_login)

    return app
