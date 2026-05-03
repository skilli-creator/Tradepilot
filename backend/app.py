from flask import Flask
from routes.bot_routes import bot_bp

def create_app():
    app = Flask(__name__)

    app.register_blueprint(bot_bp, url_prefix="/api/bot")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)