from datetime import datetime
from shared.database import db
from shared.utils import generate_id


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="customer")
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = db.relationship("UserProfile", backref="user", uselist=False, lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), unique=True, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    avatar_url = db.Column(db.String(500))
    location = db.Column(db.String(255))
    bio = db.Column(db.Text)
    wedding_date = db.Column(db.DateTime, nullable=True)
    partner_name = db.Column(db.String(200))
    budget_range = db.Column(db.String(100))
    guest_count = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "location": self.location,
            "bio": self.bio,
            "wedding_date": self.wedding_date.isoformat() if self.wedding_date else None,
            "partner_name": self.partner_name,
            "budget_range": self.budget_range,
            "guest_count": self.guest_count,
        }
