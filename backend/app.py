from flask import Flask
from backend.config import Config
from backend.routes.connect import connect_bp
from backend.routes.bot_routes import bot_bp
from flask_cors import CORS
from backend.routes.bot import bot_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(bot_bp)

    # Allow frontend requests (important for fetch + OPTIONS preflight)
    CORS(app, supports_credentials=True)

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    app.register_blueprint(connect_bp)
  

    # =========================
    # HEALTH CHECK ROUTE
    # =========================
    @app.route("/")
    def home():
        return {"message": "Tradepilot backend running 🚀"}

    return app


# =========================
# RUN APP
# =========================
if __name__ == "__main__":
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )