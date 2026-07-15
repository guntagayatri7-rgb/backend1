from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    event_type = db.Column(db.String(100))
    location = db.Column(db.String(255))
    city = db.Column(db.String(100))
    venue = db.Column(db.String(255))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    cover_image = db.Column(db.String(500))
    gallery = db.Column(db.JSON, default=list)
    capacity = db.Column(db.Integer, default=0)
    ticket_price = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="INR")
    is_free = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(50), default="upcoming")
    tags = db.Column(db.JSON, default=list)
    highlights = db.Column(db.JSON, default=list)
    include_services = db.Column(db.JSON, default=list)
    faq = db.Column(db.JSON, default=list)
    booking_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "event_type": self.event_type,
            "location": self.location,
            "city": self.city,
            "venue": self.venue,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "cover_image": self.cover_image,
            "gallery": self.gallery or [],
            "capacity": self.capacity,
            "ticket_price": self.ticket_price,
            "currency": self.currency,
            "is_free": self.is_free,
            "is_featured": self.is_featured,
            "is_active": self.is_active,
            "status": self.status,
            "tags": self.tags or [],
            "highlights": self.highlights or [],
            "include_services": self.include_services or [],
            "faq": self.faq or [],
            "booking_count": self.booking_count,
            "rating": self.rating,
            "review_count": self.review_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
