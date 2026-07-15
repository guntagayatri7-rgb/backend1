from shared.database import db
from shared.utils import generate_id


class SavedVendor(db.Model):
    __tablename__ = "saved_vendors"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    vendor_id = db.Column(db.String(36), db.ForeignKey("vendor_profiles.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("user_id", "vendor_id", name="uq_user_vendor"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vendor_id": self.vendor_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SavedEvent(db.Model):
    __tablename__ = "saved_events"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    event_id = db.Column(db.String(36), db.ForeignKey("events.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (db.UniqueConstraint("user_id", "event_id", name="uq_user_event"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "event_id": self.event_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.String(36), primary_key=True, default=generate_id)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), default="info")
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "is_read": self.is_read,
            "link": self.link,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
