import uuid

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.infra.database.base import Base


class History(Base):
    __tablename__ = "history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    service_order_id = Column(String(36), ForeignKey("service_orders.id"), nullable=True)
    part_id = Column(String(36), ForeignKey("parts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<History(id={self.id}, event_type={self.event_type})>"