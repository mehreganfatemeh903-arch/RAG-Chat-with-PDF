from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)

    name = Column(
        String(200),
        nullable=False
    )

    plan = Column(
        String(50),
        default="Free"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
