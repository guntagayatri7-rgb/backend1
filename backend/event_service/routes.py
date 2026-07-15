from flask import Blueprint, request
from datetime import datetime

from shared.database import db
from shared.utils import token_required, vendor_required, error_response, success_response, paginate
from event_service.models import Event

event_bp = Blueprint("events", __name__)


@event_bp.route("/api/events", methods=["GET"])
def list_events():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")
    city = request.args.get("city")
    event_type = request.args.get("event_type")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "upcoming")

    query = Event.query.filter_by(is_active=True)

    if status != "all":
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if city:
        query = query.filter(Event.city.ilike(f"%{city}%"))
    if event_type:
        query = query.filter_by(event_type=event_type)
    if min_price is not None:
        query = query.filter(Event.ticket_price >= min_price)
    if max_price is not None:
        query = query.filter(Event.ticket_price <= max_price)
    if search:
        query = query.filter(
            db.or_(
                Event.title.ilike(f"%{search}%"),
                Event.description.ilike(f"%{search}%"),
                Event.tags.astext.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(Event.is_featured.desc(), Event.start_date.asc())
    return success_response(paginate(query, page, per_page))


@event_bp.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event or not event.is_active:
        return error_response("Event not found", 404)
    return success_response(event.to_dict())


@event_bp.route("/api/events", methods=["POST"])
@token_required
def create_event():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile required to create events", 403)

    event = Event(
        vendor_id=vendor.id,
        title=data.get("title"),
        description=data.get("description"),
        category=data.get("category"),
        event_type=data.get("event_type"),
        location=data.get("location"),
        city=data.get("city"),
        venue=data.get("venue"),
        capacity=data.get("capacity", 0),
        ticket_price=data.get("ticket_price", 0),
        currency=data.get("currency", "INR"),
        is_free=data.get("is_free", False),
        cover_image=data.get("cover_image"),
        gallery=data.get("gallery", []),
        tags=data.get("tags", []),
        highlights=data.get("highlights", []),
        include_services=data.get("include_services", []),
        faq=data.get("faq", []),
        status=data.get("status", "upcoming"),
    )

    if "start_date" in data and data["start_date"]:
        event.start_date = datetime.fromisoformat(data["start_date"])
    if "end_date" in data and data["end_date"]:
        event.end_date = datetime.fromisoformat(data["end_date"])

    db.session.add(event)
    db.session.commit()
    return success_response(event.to_dict(), "Event created", 201)


@event_bp.route("/api/events/<event_id>", methods=["PUT"])
@token_required
def update_event(event_id):
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile required", 403)

    event = Event.query.filter_by(id=event_id, vendor_id=vendor.id).first()
    if not event:
        return error_response("Event not found", 404)

    editable = ("title", "description", "category", "event_type", "location",
                "city", "venue", "capacity", "ticket_price", "currency", "is_free",
                "is_active", "status", "cover_image", "gallery", "tags", "highlights",
                "include_services", "faq")
    for field in editable:
        if field in data:
            setattr(event, field, data[field])

    if "start_date" in data:
        event.start_date = datetime.fromisoformat(data["start_date"]) if data["start_date"] else None
    if "end_date" in data:
        event.end_date = datetime.fromisoformat(data["end_date"]) if data["end_date"] else None

    db.session.commit()
    return success_response(event.to_dict(), "Event updated")


@event_bp.route("/api/events/<event_id>", methods=["DELETE"])
@token_required
def delete_event(event_id):
    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile required", 403)

    event = Event.query.filter_by(id=event_id, vendor_id=vendor.id).first()
    if not event:
        return error_response("Event not found", 404)

    db.session.delete(event)
    db.session.commit()
    return success_response(message="Event deleted")


@event_bp.route("/api/events/my-events", methods=["GET"])
@token_required
def get_my_events():
    from vendor_service.models import VendorProfile
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile required", 403)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Event.query.filter_by(vendor_id=vendor.id).order_by(Event.created_at.desc())
    return success_response(paginate(query, page, per_page))


@event_bp.route("/api/events/featured", methods=["GET"])
def get_featured_events():
    events = Event.query.filter_by(is_active=True, is_featured=True).order_by(Event.start_date.asc()).limit(10).all()
    return success_response([e.to_dict() for e in events])


@event_bp.route("/api/events/categories", methods=["GET"])
def get_event_categories():
    categories = db.session.query(Event.category).distinct().all()
    return success_response([c[0] for c in categories if c[0]])


@event_bp.route("/api/events/upcoming", methods=["GET"])
def get_upcoming_events():
    now = datetime.utcnow()
    events = Event.query.filter(Event.is_active == True, Event.start_date >= now).order_by(Event.start_date.asc()).limit(10).all()
    return success_response([e.to_dict() for e in events])
