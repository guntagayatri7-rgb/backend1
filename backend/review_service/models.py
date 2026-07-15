from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=True)
    event_id = db.Column(db.String(36), db.ForeignKey("events.id"), nullable=True)
    booking_id = db.Column(db.String(36), db.ForeignKey("bookings.id"), nullable=True)
    review_type = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    images = db.Column(db.JSON, default=list)
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref="reviews", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vendor_id": self.vendor_id,
            "event_id": self.event_id,
            "booking_id": self.booking_id,
            "review_type": self.review_type,
            "rating": self.rating,
            "title": self.title,
            "content": self.content,
            "images": self.images or [],
            "is_verified": self.is_verified,
            "is_approved": self.is_approved,
            "helpful_count": self.helpful_count,
            "user_name": self.user.email.split("@")[0] if self.user else "Anonymous",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
