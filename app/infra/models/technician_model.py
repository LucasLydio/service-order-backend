import uuid

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.infra.database.base import Base


class Technician(Base):
    __tablename__ = "technicians"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=False, index=True)
    specialty = Column(String(100), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Technician(id={self.id}, full_name={self.full_name}, specialty={self.specialty})>"
