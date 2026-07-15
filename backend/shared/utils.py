import jwt
import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

from shared.config import Config


def generate_id():
    return str(uuid.uuid4())


def create_token(user_id, role):
    payload = {
        "sub": user_id,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=Config.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_token(token):
    try:
        return jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401
        request.user_id = payload["sub"]
        request.user_role = payload["role"]
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated


def vendor_required(f):
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        if request.user_role not in ("vendor", "admin"):
            return jsonify({"error": "Vendor access required"}), 403
        return f(*args, **kwargs)
    return decorated


def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code


def success_response(data=None, message="Success", status_code=200):
    result = {"message": message}
    if data is not None:
        result["data"] = data
    return jsonify(result), status_code


def paginate(query, page, per_page):
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
    }
