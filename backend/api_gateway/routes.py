import requests
from flask import Blueprint, request, jsonify

from shared.config import Config

gateway_bp = Blueprint("gateway", __name__)

SERVICE_URLS = {
    "auth": "http://localhost:5001",
    "users": "http://localhost:5002",
    "vendors": "http://localhost:5003",
    "events": "http://localhost:5004",
    "bookings": "http://localhost:5005",
    "payments": "http://localhost:5006",
    "reviews": "http://localhost:5007",
    "analytics": "http://localhost:5008",
}


def proxy(service, path):
    url = f"{SERVICE_URLS[service]}{path}"
    headers = {k: v for k, v in request.headers if k.lower() not in ("host", "content-length")}
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            json=request.get_json(silent=True) or None,
            timeout=30,
        )
        return jsonify(resp.json()), resp.status_code
    except requests.ConnectionError:
        return jsonify({"error": f"Service {service} unavailable"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gateway_bp.route("/api/auth/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_auth(path):
    return proxy("auth", f"/api/auth/{path}")


@gateway_bp.route("/api/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_users(path):
    return proxy("users", f"/api/users/{path}")


@gateway_bp.route("/api/vendors/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_vendors(path):
    return proxy("vendors", f"/api/vendors/{path}")


@gateway_bp.route("/api/events/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_events(path):
    return proxy("events", f"/api/events/{path}")


@gateway_bp.route("/api/bookings/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_bookings(path):
    return proxy("bookings", f"/api/bookings/{path}")


@gateway_bp.route("/api/payments/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_payments(path):
    return proxy("payments", f"/api/payments/{path}")


@gateway_bp.route("/api/reviews/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_reviews(path):
    return proxy("reviews", f"/api/reviews/{path}")


@gateway_bp.route("/api/analytics/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_analytics(path):
    return proxy("analytics", f"/api/analytics/{path}")
