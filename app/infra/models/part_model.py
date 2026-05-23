import uuid

from sqlalchemy import Column, String, DateTime, Integer, Numeric
from sqlalchemy.sql import func
from app.infra.database.base import Base


class Part(Base):
    __tablename__ = "parts"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(80), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    price = Column(Numeric(10, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Part(id={self.id}, name={self.name}, sku={self.sku})>"
