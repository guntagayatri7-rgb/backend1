from flask import Blueprint, request
from datetime import datetime

from shared.database import db
from shared.utils import token_required, vendor_required, error_response, success_response, paginate
from booking_service.models import Booking

booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/api/bookings", methods=["POST"])
@token_required
def create_booking():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    booking = Booking(
        user_id=request.user_id,
        vendor_id=data.get("vendor_id"),
        event_id=data.get("event_id"),
        service_id=data.get("service_id"),
        booking_type=data.get("booking_type", "vendor"),
        total_amount=data.get("total_amount", 0),
        currency=data.get("currency", "INR"),
        quantity=data.get("quantity", 1),
        guest_count=data.get("guest_count"),
        special_requests=data.get("special_requests"),
        contact_phone=data.get("contact_phone"),
        contact_email=data.get("contact_email"),
        status="pending",
        payment_status="pending",
    )

    if "event_date" in data and data["event_date"]:
        booking.event_date = datetime.fromisoformat(data["event_date"])

    db.session.add(booking)
    db.session.commit()

    return success_response(booking.to_dict(), "Booking created", 201)


@booking_bp.route("/api/bookings/<booking_id>", methods=["GET"])
@token_required
def get_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    if booking.user_id != request.user_id:
        from vendor_service.models import VendorProfile
        vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
        if not vendor or booking.vendor_id != vendor.id:
            return error_response("Access denied", 403)
    return success_response(booking.to_dict())


@booking_bp.route("/api/bookings/<booking_id>/status", methods=["PUT"])
@token_required
def update_booking_status(booking_id):
    data = request.get_json()
    if not data or "status" not in data:
        return error_response("Status is required")

    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()

    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found", 404)

    if not vendor or booking.vendor_id != vendor.id:
        return error_response("Access denied", 403)

    valid_statuses = ("confirmed", "in_progress", "completed", "cancelled")
    if data["status"] not in valid_statuses:
        return error_response(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    booking.status = data["status"]
    if data["status"] == "cancelled":
        booking.cancellation_reason = data.get("reason")
        booking.cancelled_at = datetime.utcnow()

    db.session.commit()
    return success_response(booking.to_dict(), "Booking status updated")


@booking_bp.route("/api/bookings/<booking_id>/cancel", methods=["PUT"])
@token_required
def cancel_booking(booking_id):
    data = request.get_json()
    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    if booking.user_id != request.user_id:
        return error_response("Access denied", 403)
    if booking.status in ("completed", "cancelled"):
        return error_response(f"Cannot cancel booking with status: {booking.status}", 400)

    booking.status = "cancelled"
    booking.cancellation_reason = data.get("reason", "") if data else ""
    booking.cancelled_at = datetime.utcnow()
    db.session.commit()
    return success_response(booking.to_dict(), "Booking cancelled")


@booking_bp.route("/api/bookings/my-bookings", methods=["GET"])
@token_required
def get_my_bookings():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Booking.query.filter_by(user_id=request.user_id)
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Booking.created_at.desc())
    return success_response(paginate(query, page, per_page))


@booking_bp.route("/api/bookings/vendor-bookings", methods=["GET"])
@token_required
def get_vendor_bookings():
    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile required", 403)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status = request.args.get("status")

    query = Booking.query.filter_by(vendor_id=vendor.id)
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Booking.created_at.desc())
    return success_response(paginate(query, page, per_page))


@booking_bp.route("/api/bookings/<booking_id>/payment", methods=["PUT"])
@token_required
def update_booking_payment(booking_id):
    data = request.get_json()
    if not data or "payment_status" not in data:
        return error_response("payment_status is required")

    booking = Booking.query.get(booking_id)
    if not booking:
        return error_response("Booking not found", 404)
    if booking.user_id != request.user_id:
        return error_response("Access denied", 403)

    booking.payment_status = data["payment_status"]
    if "payment_id" in data:
        booking.payment_id = data["payment_id"]

    db.session.commit()
    return success_response(booking.to_dict(), "Payment status updated")
