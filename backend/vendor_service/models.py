from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class VendorProfile(db.Model):
    __tablename__ = "vendor_profiles"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    business_name = db.Column(db.String(255), nullable=False)
    business_email = db.Column(db.String(255))
    business_phone = db.Column(db.String(20))
    category = db.Column(db.String(100), nullable=False)
    subcategories = db.Column(db.JSON, default=list)
    description = db.Column(db.Text)
    short_bio = db.Column(db.String(500))
    website = db.Column(db.String(500))
    location = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    service_area = db.Column(db.String(500))
    price_range = db.Column(db.String(50))
    starting_price = db.Column(db.Float, default=0)
    currency = db.Column(db.String(10), default="INR")
    cover_image = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    gallery = db.Column(db.JSON, default=list)
    years_in_business = db.Column(db.Integer, default=1)
    team_size = db.Column(db.Integer, default=1)
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    total_bookings = db.Column(db.Integer, default=0)
    social_links = db.Column(db.JSON, default=dict)
    business_hours = db.Column(db.JSON, default=dict)
    tags = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    services = db.relationship("VendorService", backref="vendor", lazy="dynamic", cascade="all, delete-orphan")
    portfolios = db.relationship("VendorPortfolio", backref="vendor", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "business_name": self.business_name,
            "business_email": self.business_email,
            "business_phone": self.business_phone,
            "category": self.category,
            "subcategories": self.subcategories or [],
            "description": self.description,
            "short_bio": self.short_bio,
            "website": self.website,
            "location": self.location,
            "city": self.city,
            "state": self.state,
            "service_area": self.service_area,
            "price_range": self.price_range,
            "starting_price": self.starting_price,
            "currency": self.currency,
            "cover_image": self.cover_image,
            "logo_url": self.logo_url,
            "gallery": self.gallery or [],
            "years_in_business": self.years_in_business,
            "team_size": self.team_size,
            "is_verified": self.is_verified,
            "is_featured": self.is_featured,
            "is_active": self.is_active,
            "rating": self.rating,
            "review_count": self.review_count,
            "total_bookings": self.total_bookings,
            "social_links": self.social_links or {},
            "business_hours": self.business_hours or {},
            "tags": self.tags or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class VendorService(db.Model):
    __tablename__ = "vendor_services"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)
    duration = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "duration": self.duration,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class VendorPortfolio(db.Model):
    __tablename__ = "vendor_portfolios"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    images = db.Column(db.JSON, default=list)
    event_type = db.Column(db.String(100))
    client_name = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "title": self.title,
            "description": self.description,
            "images": self.images or [],
            "event_type": self.event_type,
            "client_name": self.client_name,
            "date": self.date.isoformat() if self.date else None,
            "is_featured": self.is_featured,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
