from flask import Flask
from backend.config import Config
from backend.routes.connect import connect_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)  # 🔥 allow frontend access

    app.register_blueprint(connect_bp)

    @app.route("/")
    def home():
        return {"message": "Tradepilot backend running 🚀"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
