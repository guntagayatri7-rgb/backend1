import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS
from shared.config import Config
from api_gateway.routes import gateway_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    app.register_blueprint(gateway_bp)

    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "api_gateway"}

    @app.route("/")
    def index():
        return {
            "name": "CelebrateHub API Gateway",
            "version": "1.0.0",
            "endpoints": {
                "auth": "/api/auth/*",
                "users": "/api/users/*",
                "vendors": "/api/vendors/*",
                "events": "/api/events/*",
                "bookings": "/api/bookings/*",
                "payments": "/api/payments/*",
                "reviews": "/api/reviews/*",
                "analytics": "/api/analytics/*",
            },
        }

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
