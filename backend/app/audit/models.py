from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer
    )

    action = Column(
        String(200)
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
