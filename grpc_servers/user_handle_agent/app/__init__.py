from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from .routes import routes_bp
    app.register_blueprint(routes_bp)
    
    return app
