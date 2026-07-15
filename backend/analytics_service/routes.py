from flask import Blueprint, request
from datetime import datetime, timedelta

from shared.database import db
from shared.utils import token_required, vendor_required, error_response, success_response

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/api/analytics/dashboard", methods=["GET"])
@token_required
def get_dashboard():
    from auth_service.models import User
    from vendor_service.models import VendorProfile
    from event_service.models import Event
    from booking_service.models import Booking
    from review_service.models import Review

    total_users = User.query.count()
    total_vendors = VendorProfile.query.count()
    total_events = Event.query.filter_by(is_active=True).count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.status == "completed"
    ).scalar() or 0
    total_reviews = Review.query.count()

    return success_response({
        "total_users": total_users,
        "total_vendors": total_vendors,
        "total_events": total_events,
        "total_bookings": total_bookings,
        "total_revenue": float(total_revenue),
        "total_reviews": total_reviews,
    })


@analytics_bp.route("/api/analytics/vendor", methods=["GET"])
@token_required
def get_vendor_analytics():
    from vendor_service.models import VendorProfile
    from booking_service.models import Booking
    from review_service.models import Review
    from event_service.models import Event

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    period = request.args.get("period", "30")

    days = int(period)
    since = datetime.utcnow() - timedelta(days=days)

    total_bookings = Booking.query.filter_by(vendor_id=vendor.id).count()
    completed_bookings = Booking.query.filter_by(vendor_id=vendor.id, status="completed").count()
    pending_bookings = Booking.query.filter_by(vendor_id=vendor.id, status="pending").count()
    cancelled_bookings = Booking.query.filter_by(vendor_id=vendor.id, status="cancelled").count()

    revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.vendor_id == vendor.id,
        Booking.status == "completed",
        Booking.created_at >= since,
    ).scalar() or 0

    total_views = vendor.total_bookings or 0
    total_reviews = Review.query.filter_by(vendor_id=vendor.id).count()
    average_rating = vendor.rating or 0

    events_count = Event.query.filter_by(vendor_id=vendor.id, is_active=True).count()

    booking_trends = db.session.query(
        db.func.date(Booking.created_at).label("date"),
        db.func.count(Booking.id).label("count"),
    ).filter(
        Booking.vendor_id == vendor.id,
        Booking.created_at >= since,
    ).group_by(db.func.date(Booking.created_at)).order_by("date").all()

    return success_response({
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "pending_bookings": pending_bookings,
        "cancelled_bookings": cancelled_bookings,
        "revenue": float(revenue),
        "total_views": total_views,
        "total_reviews": total_reviews,
        "average_rating": float(average_rating),
        "events_count": events_count,
        "booking_trends": [
            {"date": str(t.date), "count": t.count} for t in booking_trends
        ],
    })


@analytics_bp.route("/api/analytics/revenue", methods=["GET"])
@token_required
def get_revenue_analytics():
    from booking_service.models import Booking

    period = request.args.get("period", "30")
    days = int(period)
    since = datetime.utcnow() - timedelta(days=days)

    if request.user_role == "vendor":
        from vendor_service.models import VendorProfile
        vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
        if not vendor:
            return error_response("Vendor profile not found", 404)
        base_query = Booking.query.filter_by(vendor_id=vendor.id)
    else:
        base_query = Booking.query

    revenue_data = base_query.with_entities(
        db.func.date(Booking.created_at).label("date"),
        db.func.sum(Booking.total_amount).label("revenue"),
        db.func.count(Booking.id).label("bookings"),
    ).filter(
        Booking.status == "completed",
        Booking.created_at >= since,
    ).group_by(db.func.date(Booking.created_at)).order_by("date").all()

    return success_response({
        "period": f"{days}_days",
        "data": [
            {
                "date": str(r.date),
                "revenue": float(r.revenue or 0),
                "bookings": r.bookings,
            }
            for r in revenue_data
        ],
    })


@analytics_bp.route("/api/analytics/popular-vendors", methods=["GET"])
def get_popular_vendors():
    from vendor_service.models import VendorProfile

    limit = request.args.get("limit", 10, type=int)
    vendors = VendorProfile.query.filter_by(is_active=True).order_by(
        VendorProfile.total_bookings.desc(),
        VendorProfile.rating.desc(),
    ).limit(limit).all()

    return success_response([{
        "id": v.id,
        "business_name": v.business_name,
        "category": v.category,
        "rating": v.rating,
        "total_bookings": v.total_bookings,
        "review_count": v.review_count,
        "cover_image": v.cover_image,
        "city": v.city,
    } for v in vendors])


@analytics_bp.route("/api/analytics/popular-categories", methods=["GET"])
def get_popular_categories():
    from vendor_service.models import VendorProfile
    from booking_service.models import Booking

    categories = db.session.query(
        VendorProfile.category,
        db.func.count(Booking.id).label("booking_count"),
    ).outerjoin(Booking, Booking.vendor_id == VendorProfile.id).filter(
        VendorProfile.is_active == True,
        VendorProfile.category.isnot(None),
    ).group_by(VendorProfile.category).order_by(db.text("booking_count DESC")).all()

    return success_response([
        {"category": c[0], "booking_count": c[1]} for c in categories if c[0]
    ])
