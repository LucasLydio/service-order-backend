import uuid

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from app.infra.database.base import Base
import enum


class ServiceOrderStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ServiceOrderStatus), default=ServiceOrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ServiceOrder(id={self.id}, customer_id={self.customer_id})>"
