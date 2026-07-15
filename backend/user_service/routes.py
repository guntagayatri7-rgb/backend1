from flask import Blueprint, request

from shared.database import db
from shared.utils import token_required, error_response, success_response, paginate
from user_service.models import SavedVendor, SavedEvent, Notification
from auth_service.models import User, UserProfile

user_bp = Blueprint("users", __name__)


@user_bp.route("/api/users/profile", methods=["GET"])
@token_required
def get_profile():
    user = User.query.get(request.user_id)
    if not user:
        return error_response("User not found", 404)
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    result = user.to_dict()
    if profile:
        result["profile"] = profile.to_dict()
    return success_response(result)


@user_bp.route("/api/users/profile", methods=["PUT"])
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
    if "wedding_date" in data:
        from datetime import datetime
        profile.wedding_date = datetime.fromisoformat(data["wedding_date"]) if data["wedding_date"] else None

    db.session.commit()
    return success_response(profile.to_dict(), "Profile updated")


@user_bp.route("/api/users/saved-vendors", methods=["GET"])
@token_required
def get_saved_vendors():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = SavedVendor.query.filter_by(user_id=request.user_id).order_by(SavedVendor.created_at.desc())
    return success_response(paginate(query, page, per_page))


@user_bp.route("/api/users/saved-vendors/<vendor_id>", methods=["POST"])
@token_required
def save_vendor(vendor_id):
    existing = SavedVendor.query.filter_by(user_id=request.user_id, vendor_id=vendor_id).first()
    if existing:
        return error_response("Vendor already saved", 409)
    saved = SavedVendor(user_id=request.user_id, vendor_id=vendor_id)
    db.session.add(saved)
    db.session.commit()
    return success_response(saved.to_dict(), "Vendor saved", 201)


@user_bp.route("/api/users/saved-vendors/<vendor_id>", methods=["DELETE"])
@token_required
def remove_saved_vendor(vendor_id):
    saved = SavedVendor.query.filter_by(user_id=request.user_id, vendor_id=vendor_id).first()
    if not saved:
        return error_response("Saved vendor not found", 404)
    db.session.delete(saved)
    db.session.commit()
    return success_response(message="Vendor removed from saved")


@user_bp.route("/api/users/saved-events", methods=["GET"])
@token_required
def get_saved_events():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = SavedEvent.query.filter_by(user_id=request.user_id).order_by(SavedEvent.created_at.desc())
    return success_response(paginate(query, page, per_page))


@user_bp.route("/api/users/saved-events/<event_id>", methods=["POST"])
@token_required
def save_event(event_id):
    existing = SavedEvent.query.filter_by(user_id=request.user_id, event_id=event_id).first()
    if existing:
        return error_response("Event already saved", 409)
    saved = SavedEvent(user_id=request.user_id, event_id=event_id)
    db.session.add(saved)
    db.session.commit()
    return success_response(saved.to_dict(), "Event saved", 201)


@user_bp.route("/api/users/saved-events/<event_id>", methods=["DELETE"])
@token_required
def remove_saved_event(event_id):
    saved = SavedEvent.query.filter_by(user_id=request.user_id, event_id=event_id).first()
    if not saved:
        return error_response("Saved event not found", 404)
    db.session.delete(saved)
    db.session.commit()
    return success_response(message="Event removed from saved")


@user_bp.route("/api/users/notifications", methods=["GET"])
@token_required
def get_notifications():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Notification.query.filter_by(user_id=request.user_id).order_by(Notification.created_at.desc())
    return success_response(paginate(query, page, per_page))


@user_bp.route("/api/users/notifications/<notification_id>/read", methods=["PUT"])
@token_required
def mark_notification_read(notification_id):
    notif = Notification.query.filter_by(id=notification_id, user_id=request.user_id).first()
    if not notif:
        return error_response("Notification not found", 404)
    notif.is_read = True
    db.session.commit()
    return success_response(notif.to_dict(), "Notification marked as read")


@user_bp.route("/api/users/notifications/read-all", methods=["PUT"])
@token_required
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=request.user_id, is_read=False).update({"is_read": True})
    db.session.commit()
    return success_response(message="All notifications marked as read")
