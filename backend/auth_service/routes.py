from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from shared.database import db
from shared.utils import create_token, decode_token, token_required, error_response, success_response
from auth_service.models import User, UserProfile

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "customer")

    if not email or not password:
        return error_response("Email and password are required")
    if len(password) < 6:
        return error_response("Password must be at least 6 characters")
    if role not in ("customer", "vendor", "admin"):
        return error_response("Invalid role")

    existing = User.query.filter_by(email=email).first()
    if existing:
        return error_response("Email already registered", 409)

    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role,
    )
    db.session.add(user)
    db.session.flush()

    profile = UserProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()

    token = create_token(user.id, user.role)
    return success_response({
        "token": token,
        "user": user.to_dict(),
    }, "Registration successful", 201)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return error_response("Email and password are required")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return error_response("Invalid email or password", 401)
    if not user.is_active:
        return error_response("Account is deactivated", 403)

    token = create_token(user.id, user.role)
    return success_response({
        "token": token,
        "user": user.to_dict(),
    }, "Login successful")


@auth_bp.route("/api/auth/me", methods=["GET"])
@token_required
def get_current_user():
    user = User.query.get(request.user_id)
    if not user:
        return error_response("User not found", 404)
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    result = user.to_dict()
    if profile:
        result["profile"] = profile.to_dict()
    return success_response(result)


@auth_bp.route("/api/auth/verify-token", methods=["POST"])
def verify_token():
    data = request.get_json()
    token = data.get("token", "") if data else ""
    payload = decode_token(token)
    if not payload:
        return error_response("Invalid or expired token", 401)
    user = User.query.get(payload["sub"])
    if not user:
        return error_response("User not found", 404)
    return success_response({"valid": True, "user": user.to_dict()})


@auth_bp.route("/api/auth/update-profile", methods=["PUT"])
@token_required
def update_profile():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    profile = UserProfile.query.filter_by(user_id=request.user_id).first()
    if not profile:
        return error_response("Profile not found", 404)

    editable = ("first_name", "last_name", "phone", "avatar_url", "location",
                "bio", "partner_name", "budget_range", "guest_count")
    for field in editable:
        if field in data:
            setattr(profile, field, data[field])

    if "wedding_date" in data and data["wedding_date"]:
        profile.wedding_date = datetime.fromisoformat(data["wedding_date"])

    db.session.commit()
    return success_response(profile.to_dict(), "Profile updated")
