from sqlalchemy import Column, Integer, String, Text, Float

from app.db.base import Base


class DocumentAnalysis(Base):

    __tablename__ = "document_analysis"

    id = Column(
        Integer,
        primary_key=True
    )

    document_id = Column(
        Integer,
        nullable=False
    )

    document_type = Column(
        String(100)
    )

    extracted_data = Column(
        Text
    )

    confidence = Column(
        Float,
        default=0
    )
