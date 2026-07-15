from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    booking_id = db.Column(db.String(36), db.ForeignKey("bookings.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default="INR")
    gateway = db.Column(db.String(50), default="razorpay")
    gateway_payment_id = db.Column(db.String(255))
    gateway_order_id = db.Column(db.String(255))
    gateway_signature = db.Column(db.String(500))
    status = db.Column(db.String(50), default="pending")
    payment_method = db.Column(db.String(100))
    receipt_url = db.Column(db.String(500))
    description = db.Column(db.String(500))
    metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "booking_id": self.booking_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "gateway": self.gateway,
            "gateway_payment_id": self.gateway_payment_id,
            "gateway_order_id": self.gateway_order_id,
            "status": self.status,
            "payment_method": self.payment_method,
            "receipt_url": self.receipt_url,
            "description": self.description,
            "metadata": self.metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Refund(db.Model):
    __tablename__ = "refunds"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    payment_id = db.Column(db.String(36), db.ForeignKey("payments.id"), nullable=False)
    booking_id = db.Column(db.String(36), db.ForeignKey("bookings.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    reason = db.Column(db.Text)
    gateway_refund_id = db.Column(db.String(255))
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "payment_id": self.payment_id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "reason": self.reason,
            "gateway_refund_id": self.gateway_refund_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
