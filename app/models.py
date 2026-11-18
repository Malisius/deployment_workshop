from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Item(db.Model):
    """Demonstration entity stored in the MySQL database."""
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default="general")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DeploymentLog(db.Model):
    """Audit log recording database creation, seeding, and app startup events."""
    __tablename__ = "deployment_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "event": self.event,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
