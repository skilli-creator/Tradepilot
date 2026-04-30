from flask import Flask
from backend.routes.bot_routes import bot_bp

def create_app():

    app = Flask(__name__)

    app.register_blueprint(bot_bp)

    return app