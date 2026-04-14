import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(length=255), nullable=False)
    content = Column(Text, nullable=False)
    source_url = Column(String(length=500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
