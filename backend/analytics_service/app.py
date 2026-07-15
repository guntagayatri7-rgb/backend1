import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from shared.config import Config
from shared.database import init_db
from analytics_service.routes import analytics_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    init_db(app)

    app.register_blueprint(analytics_bp)

    @app.route("/api/analytics/health")
    def health():
        return {"status": "healthy", "service": "analytics_service"}

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5008, debug=Config.DEBUG)
