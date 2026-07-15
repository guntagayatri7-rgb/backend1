from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=True)
    event_id = db.Column(db.String(36), db.ForeignKey("events.id"), nullable=True)
    service_id = db.Column(db.String(36), nullable=True)
    booking_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="pending")
    total_amount = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="INR")
    quantity = db.Column(db.Integer, default=1)
    guest_count = db.Column(db.Integer, nullable=True)
    event_date = db.Column(db.DateTime)
    special_requests = db.Column(db.Text)
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(255))
    payment_status = db.Column(db.String(50), default="pending")
    payment_id = db.Column(db.String(255), nullable=True)
    cancellation_reason = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vendor_id": self.vendor_id,
            "event_id": self.event_id,
            "service_id": self.service_id,
            "booking_type": self.booking_type,
            "status": self.status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "quantity": self.quantity,
            "guest_count": self.guest_count,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "special_requests": self.special_requests,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "payment_status": self.payment_status,
            "payment_id": self.payment_id,
            "cancellation_reason": self.cancellation_reason,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
