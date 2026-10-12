from datetime import datetime, timezone
from extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class AuditLog(db.Model):
    """Audit log for system security, administrative inspection, and tracking operations."""
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=utc_now, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="audit_logs")

    @classmethod
    def log(cls, action, user_id=None, ip_address=None, details=None):
        """Helper method to easily append an audit entry."""
        entry = cls(
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details,
        )
        db.session.add(entry)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    def __repr__(self):
        return f"<AuditLog {self.action} by user={self.user_id} at {self.timestamp}>"
