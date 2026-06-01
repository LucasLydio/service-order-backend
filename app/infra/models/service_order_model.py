import enum
import uuid

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum, Integer
from sqlalchemy.sql import func
from app.infra.database.base import Base


class ServiceOrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ServiceOrderPriority(str, enum.Enum):
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class ServiceOrder(Base):
    __tablename__ = "service_orders"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    technician_id = Column(String(36), ForeignKey("technicians.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ServiceOrderStatus), default=ServiceOrderStatus.PENDING)
    priority = Column(Enum(ServiceOrderPriority), default=ServiceOrderPriority.MEDIA)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    service_time_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<ServiceOrder(id={self.id}, customer_id={self.customer_id}, status={self.status})>"
