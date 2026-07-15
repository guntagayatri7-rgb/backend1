import uuid
from flask import Blueprint, request

from shared.database import db
from shared.utils import token_required, error_response, success_response, paginate
from payment_service.models import Payment, Refund

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/api/payments/create-order", methods=["POST"])
@token_required
def create_order():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    amount = data.get("amount")
    booking_id = data.get("booking_id")
    gateway = data.get("gateway", "razorpay")

    if not amount or not booking_id:
        return error_response("amount and booking_id are required")

    payment = Payment(
        booking_id=booking_id,
        user_id=request.user_id,
        amount=amount,
        currency=data.get("currency", "INR"),
        gateway=gateway,
        status="created",
        description=data.get("description", ""),
        metadata=data.get("metadata", {}),
    )

    payment.gateway_order_id = f"order_{uuid.uuid4().hex[:16]}"

    db.session.add(payment)
    db.session.commit()

    return success_response({
        "payment_id": payment.id,
        "order_id": payment.gateway_order_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "gateway": payment.gateway,
    }, "Payment order created", 201)


@payment_bp.route("/api/payments/verify", methods=["POST"])
@token_required
def verify_payment():
    data = request.get_json()
    if not data:
        return error_response("Request body is required")

    payment_id = data.get("payment_id")
    gateway_payment_id = data.get("gateway_payment_id")
    gateway_signature = data.get("gateway_signature")

    if not payment_id or not gateway_payment_id:
        return error_response("payment_id and gateway_payment_id are required")

    payment = Payment.query.get(payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    if payment.user_id != request.user_id:
        return error_response("Access denied", 403)

    payment.gateway_payment_id = gateway_payment_id
    payment.gateway_signature = gateway_signature
    payment.status = "completed"
    payment.payment_method = data.get("payment_method")

    from booking_service.models import Booking
    booking = Booking.query.get(payment.booking_id)
    if booking:
        booking.payment_status = "completed"
        booking.payment_id = payment.id
        if booking.status == "pending":
            booking.status = "confirmed"

    db.session.commit()
    return success_response(payment.to_dict(), "Payment verified successfully")


@payment_bp.route("/api/payments/<payment_id>", methods=["GET"])
@token_required
def get_payment(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    if payment.user_id != request.user_id:
        return error_response("Access denied", 403)
    return success_response(payment.to_dict())


@payment_bp.route("/api/payments/my-payments", methods=["GET"])
@token_required
def get_my_payments():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Payment.query.filter_by(user_id=request.user_id).order_by(Payment.created_at.desc())
    return success_response(paginate(query, page, per_page))


@payment_bp.route("/api/payments/<payment_id>/refund", methods=["POST"])
@token_required
def refund_payment(payment_id):
    data = request.get_json()

    payment = Payment.query.get(payment_id)
    if not payment:
        return error_response("Payment not found", 404)
    if payment.status != "completed":
        return error_response("Payment is not completed", 400)

    refund_amount = data.get("amount", payment.amount) if data else payment.amount

    refund = Refund(
        payment_id=payment.id,
        booking_id=payment.booking_id,
        amount=refund_amount,
        reason=data.get("reason", "") if data else "",
        gateway_refund_id=f"refund_{uuid.uuid4().hex[:16]}",
        status="processed",
    )

    payment.status = "refunded"

    from booking_service.models import Booking
    booking = Booking.query.get(payment.booking_id)
    if booking:
        booking.payment_status = "refunded"

    db.session.add(refund)
    db.session.commit()
    return success_response(refund.to_dict(), "Refund processed")


@payment_bp.route("/api/payments/transactions", methods=["GET"])
@token_required
def get_transactions():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = Payment.query.filter_by(user_id=request.user_id).order_by(Payment.created_at.desc())
    return success_response(paginate(query, page, per_page))
