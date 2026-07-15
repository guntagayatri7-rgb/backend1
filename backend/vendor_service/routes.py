from flask import Blueprint, request

from shared.database import db
from shared.utils import token_required, vendor_required, error_response, success_response, paginate
from vendor_service.models import VendorProfile, VendorService, VendorPortfolio
from auth_service.models import User

vendor_bp = Blueprint("vendors", __name__)


@vendor_bp.route("/api/vendors", methods=["GET"])
def list_vendors():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    category = request.args.get("category")
    city = request.args.get("city")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    rating = request.args.get("min_rating", type=float)
    search = request.args.get("search", "").strip()

    query = VendorProfile.query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)
    if city:
        query = query.filter(VendorProfile.city.ilike(f"%{city}%"))
    if min_price is not None:
        query = query.filter(VendorProfile.starting_price >= min_price)
    if max_price is not None:
        query = query.filter(VendorProfile.starting_price <= max_price)
    if rating is not None:
        query = query.filter(VendorProfile.rating >= rating)
    if search:
        query = query.filter(
            db.or_(
                VendorProfile.business_name.ilike(f"%{search}%"),
                VendorProfile.description.ilike(f"%{search}%"),
                VendorProfile.tags.astext.ilike(f"%{search}%"),
            )
        )

    query = query.order_by(VendorProfile.is_featured.desc(), VendorProfile.rating.desc())
    return success_response(paginate(query, page, per_page))


@vendor_bp.route("/api/vendors/<vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    vendor = VendorProfile.query.get(vendor_id)
    if not vendor or not vendor.is_active:
        return error_response("Vendor not found", 404)
    result = vendor.to_dict()
    result["services"] = [s.to_dict() for s in vendor.services.filter_by(is_active=True).all()]
    result["portfolio"] = [p.to_dict() for p in vendor.portfolios.order_by(VendorPortfolio.created_at.desc()).limit(10).all()]
    return success_response(result)


@vendor_bp.route("/api/vendors/profile", methods=["GET"])
@token_required
def get_my_vendor_profile():
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found. Please register as a vendor first.", 404)
    result = vendor.to_dict()
    result["services"] = [s.to_dict() for s in vendor.services.all()]
    result["portfolio"] = [p.to_dict() for p in vendor.portfolios.order_by(VendorPortfolio.created_at.desc()).all()]
    return success_response(result)


@vendor_bp.route("/api/vendors/profile", methods=["POST"])
@token_required
def create_vendor_profile():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    existing = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if existing:
        return error_response("Vendor profile already exists", 409)

    vendor = VendorProfile(
        user_id=request.user_id,
        business_name=data.get("business_name"),
        category=data.get("category"),
    )

    editable = ("business_email", "business_phone", "subcategories", "description",
                "short_bio", "website", "location", "city", "state", "service_area",
                "price_range", "starting_price", "currency", "cover_image", "logo_url",
                "gallery", "years_in_business", "team_size", "social_links",
                "business_hours", "tags")
    for field in editable:
        if field in data:
            setattr(vendor, field, data[field])

    db.session.add(vendor)
    db.session.commit()

    user = User.query.get(request.user_id)
    if user and user.role == "customer":
        user.role = "vendor"
        db.session.commit()

    return success_response(vendor.to_dict(), "Vendor profile created", 201)


@vendor_bp.route("/api/vendors/profile", methods=["PUT"])
@token_required
def update_vendor_profile():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    editable = ("business_name", "business_email", "business_phone", "category",
                "subcategories", "description", "short_bio", "website", "location",
                "city", "state", "service_area", "price_range", "starting_price",
                "currency", "cover_image", "logo_url", "gallery", "years_in_business",
                "team_size", "social_links", "business_hours", "tags")
    for field in editable:
        if field in data:
            setattr(vendor, field, data[field])

    db.session.commit()
    return success_response(vendor.to_dict(), "Vendor profile updated")


@vendor_bp.route("/api/vendors/services", methods=["GET"])
@token_required
def get_my_services():
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)
    services = VendorService.query.filter_by(vendor_id=vendor.id).all()
    return success_response([s.to_dict() for s in services])


@vendor_bp.route("/api/vendors/services", methods=["POST"])
@token_required
def create_service():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    service = VendorService(
        vendor_id=vendor.id,
        name=data.get("name"),
        description=data.get("description"),
        price=data.get("price", 0),
        duration=data.get("duration"),
    )
    db.session.add(service)
    db.session.commit()
    return success_response(service.to_dict(), "Service created", 201)


@vendor_bp.route("/api/vendors/services/<service_id>", methods=["PUT"])
@token_required
def update_service(service_id):
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    service = VendorService.query.filter_by(id=service_id, vendor_id=vendor.id).first()
    if not service:
        return error_response("Service not found", 404)

    for field in ("name", "description", "price", "duration", "is_active"):
        if field in data:
            setattr(service, field, data[field])

    db.session.commit()
    return success_response(service.to_dict(), "Service updated")


@vendor_bp.route("/api/vendors/services/<service_id>", methods=["DELETE"])
@token_required
def delete_service(service_id):
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    service = VendorService.query.filter_by(id=service_id, vendor_id=vendor.id).first()
    if not service:
        return error_response("Service not found", 404)

    db.session.delete(service)
    db.session.commit()
    return success_response(message="Service deleted")


@vendor_bp.route("/api/vendors/portfolio", methods=["GET"])
@token_required
def get_my_portfolio():
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)
    items = VendorPortfolio.query.filter_by(vendor_id=vendor.id).order_by(VendorPortfolio.created_at.desc()).all()
    return success_response([p.to_dict() for p in items])


@vendor_bp.route("/api/vendors/portfolio", methods=["POST"])
@token_required
def create_portfolio_item():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    from datetime import datetime
    item = VendorPortfolio(
        vendor_id=vendor.id,
        title=data.get("title"),
        description=data.get("description"),
        images=data.get("images", []),
        event_type=data.get("event_type"),
        client_name=data.get("client_name"),
        is_featured=data.get("is_featured", False),
    )
    if "date" in data and data["date"]:
        item.date = datetime.fromisoformat(data["date"])
    db.session.add(item)
    db.session.commit()
    return success_response(item.to_dict(), "Portfolio item created", 201)


@vendor_bp.route("/api/vendors/portfolio/<item_id>", methods=["PUT"])
@token_required
def update_portfolio_item(item_id):
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    item = VendorPortfolio.query.filter_by(id=item_id, vendor_id=vendor.id).first()
    if not item:
        return error_response("Portfolio item not found", 404)

    for field in ("title", "description", "images", "event_type", "client_name", "is_featured"):
        if field in data:
            setattr(item, field, data[field])
    if "date" in data:
        from datetime import datetime
        item.date = datetime.fromisoformat(data["date"]) if data["date"] else None

    db.session.commit()
    return success_response(item.to_dict(), "Portfolio item updated")


@vendor_bp.route("/api/vendors/portfolio/<item_id>", methods=["DELETE"])
@token_required
def delete_portfolio_item(item_id):
    vendor = VendorProfile.query.filter_by(user_id=request.user_id).first()
    if not vendor:
        return error_response("Vendor profile not found", 404)

    item = VendorPortfolio.query.filter_by(id=item_id, vendor_id=vendor.id).first()
    if not item:
        return error_response("Portfolio item not found", 404)

    db.session.delete(item)
    db.session.commit()
    return success_response(message="Portfolio item deleted")


@vendor_bp.route("/api/vendors/categories", methods=["GET"])
def get_categories():
    categories = db.session.query(VendorProfile.category).distinct().all()
    return success_response([c[0] for c in categories if c[0]])


@vendor_bp.route("/api/vendors/featured", methods=["GET"])
def get_featured_vendors():
    vendors = VendorProfile.query.filter_by(is_active=True, is_featured=True).order_by(VendorProfile.rating.desc()).limit(10).all()
    return success_response([v.to_dict() for v in vendors])
