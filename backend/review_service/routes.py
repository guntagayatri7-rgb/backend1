from flask import Blueprint, request

from shared.database import db
from shared.utils import token_required, error_response, success_response, paginate
from review_service.models import Review

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/api/reviews", methods=["POST"])
@token_required
def create_review():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    rating = data.get("rating")
    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return error_response("Rating must be between 1 and 5")

    review = Review(
        user_id=request.user_id,
        vendor_id=data.get("vendor_id"),
        event_id=data.get("event_id"),
        booking_id=data.get("booking_id"),
        review_type=data.get("review_type", "vendor"),
        rating=rating,
        title=data.get("title"),
        content=data.get("content"),
        images=data.get("images", []),
    )

    db.session.add(review)
    db.session.commit()

    if review.vendor_id:
        _update_vendor_rating(review.vendor_id)
    if review.event_id:
        _update_event_rating(review.event_id)

    return success_response(review.to_dict(), "Review created", 201)


@review_bp.route("/api/reviews/vendor/<vendor_id>", methods=["GET"])
def get_vendor_reviews(vendor_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Review.query.filter_by(vendor_id=vendor_id, is_approved=True).order_by(Review.created_at.desc())
    return success_response(paginate(query, page, per_page))


@review_bp.route("/api/reviews/event/<event_id>", methods=["GET"])
def get_event_reviews(event_id):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Review.query.filter_by(event_id=event_id, is_approved=True).order_by(Review.created_at.desc())
    return success_response(paginate(query, page, per_page))


@review_bp.route("/api/reviews/<review_id>", methods=["PUT"])
@token_required
def update_review(review_id):
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    review = Review.query.get(review_id)
    if not review:
        return error_response("Review not found", 404)
    if review.user_id != request.user_id:
        return error_response("Access denied", 403)

    for field in ("rating", "title", "content", "images"):
        if field in data:
            setattr(review, field, data[field])

    db.session.commit()

    if review.vendor_id:
        _update_vendor_rating(review.vendor_id)
    if review.event_id:
        _update_event_rating(review.event_id)

    return success_response(review.to_dict(), "Review updated")


@review_bp.route("/api/reviews/<review_id>", methods=["DELETE"])
@token_required
def delete_review(review_id):
    review = Review.query.get(review_id)
    if not review:
        return error_response("Review not found", 404)
    if review.user_id != request.user_id:
        return error_response("Access denied", 403)

    vendor_id = review.vendor_id
    event_id = review.event_id

    db.session.delete(review)
    db.session.commit()

    if vendor_id:
        _update_vendor_rating(vendor_id)
    if event_id:
        _update_event_rating(event_id)

    return success_response(message="Review deleted")


@review_bp.route("/api/reviews/my-reviews", methods=["GET"])
@token_required
def get_my_reviews():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Review.query.filter_by(user_id=request.user_id).order_by(Review.created_at.desc())
    return success_response(paginate(query, page, per_page))


@review_bp.route("/api/reviews/<review_id>/helpful", methods=["POST"])
@token_required
def mark_helpful(review_id):
    review = Review.query.get(review_id)
    if not review:
        return error_response("Review not found", 404)
    review.helpful_count = (review.helpful_count or 0) + 1
    db.session.commit()
    return success_response({"helpful_count": review.helpful_count}, "Marked as helpful")


@review_bp.route("/api/reviews/summary/<vendor_id>", methods=["GET"])
def get_review_summary(vendor_id):
    stats = db.session.query(
        db.func.count(Review.id).label("total"),
        db.func.avg(Review.rating).label("average"),
        db.func.sum(db.cast(db.text("rating = 5"), db.Integer)).label("five_star"),
        db.func.sum(db.cast(db.text("rating = 4"), db.Integer)).label("four_star"),
        db.func.sum(db.cast(db.text("rating = 3"), db.Integer)).label("three_star"),
        db.func.sum(db.cast(db.text("rating = 2"), db.Integer)).label("two_star"),
        db.func.sum(db.cast(db.text("rating = 1"), db.Integer)).label("one_star"),
    ).filter(Review.vendor_id == vendor_id, Review.is_approved == True).first()

    return success_response({
        "total": stats.total or 0,
        "average": round(float(stats.average or 0), 1),
        "distribution": {
            "5": stats.five_star or 0,
            "4": stats.four_star or 0,
            "3": stats.three_star or 0,
            "2": stats.two_star or 0,
            "1": stats.one_star or 0,
        },
    })


def _update_vendor_rating(vendor_id):
    from vendor_service.models import VendorProfile
    stats = db.session.query(
        db.func.avg(Review.rating),
        db.func.count(Review.id),
    ).filter(
        Review.vendor_id == vendor_id,
        Review.is_approved == True,
    ).first()
    vendor = VendorProfile.query.get(vendor_id)
    if vendor:
        vendor.rating = round(float(stats[0] or 0), 2)
        vendor.review_count = stats[1] or 0
        db.session.commit()


def _update_event_rating(event_id):
    from event_service.models import Event
    stats = db.session.query(
        db.func.avg(Review.rating),
        db.func.count(Review.id),
    ).filter(
        Review.event_id == event_id,
        Review.is_approved == True,
    ).first()
    event = Event.query.get(event_id)
    if event:
        event.rating = round(float(stats[0] or 0), 2)
        event.review_count = stats[1] or 0
        db.session.commit()
