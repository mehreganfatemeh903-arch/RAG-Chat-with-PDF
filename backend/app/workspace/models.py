from sqlalchemy import Column, Integer, String, ForeignKey

from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id")
    )
