import uuid

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from app.infra.database.base import Base


class OrderPart(Base):
    __tablename__ = "order_parts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_order_id = Column(String(36), ForeignKey("service_orders.id"), nullable=False)
    part_id = Column(String(36), ForeignKey("parts.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<OrderPart(id={self.id}, service_order_id={self.service_order_id}, part_id={self.part_id})>"