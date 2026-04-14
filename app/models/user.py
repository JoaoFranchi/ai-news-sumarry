import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=120), nullable=False)
    email = Column(String(length=255), unique=True, nullable=False, index=True)
    password_hash = Column(String(length=255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
