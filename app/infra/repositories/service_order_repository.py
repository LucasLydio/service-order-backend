from sqlalchemy.orm import Session
from app.infra.models.service_order_model import ServiceOrder, ServiceOrderStatus, ServiceOrderPriority


class ServiceOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, order_id: str) -> ServiceOrder:
        return self.db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()

    def find_by_customer_id(self, customer_id: str) -> list:
        return self.db.query(ServiceOrder).filter(ServiceOrder.customer_id == customer_id).all()

    def find_by_technician_id(self, technician_id: str) -> list:
        return self.db.query(ServiceOrder).filter(ServiceOrder.technician_id == technician_id).all()

    def create(self, customer_id: str, equipment: str, description: str = None, priority: str = "MEDIA") -> ServiceOrder:
        order = ServiceOrder(
            customer_id=customer_id,
            equipment=equipment,
            description=description,
            priority=ServiceOrderPriority(priority),
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: str, **kwargs) -> ServiceOrder:
        order = self.find_by_id(order_id)
        if not order:
            return None

        if "status" in kwargs and kwargs["status"] is not None:
            kwargs["status"] = ServiceOrderStatus(kwargs["status"])
        if "priority" in kwargs and kwargs["priority"] is not None:
            kwargs["priority"] = ServiceOrderPriority(kwargs["priority"])

        for key, value in kwargs.items():
            setattr(order, key, value)
        self.db.commit()
        self.db.refresh(order)
        return order

    def assign_technician(self, order_id: str, technician_id: str) -> ServiceOrder:
        order = self.find_by_id(order_id)
        if not order:
            return None
        order.technician_id = technician_id
        order.status = ServiceOrderStatus.IN_PROGRESS
        self.db.commit()
        self.db.refresh(order)
        return order

    def delete(self, order_id: str) -> bool:
        order = self.find_by_id(order_id)
        if order:
            self.db.delete(order)
            self.db.commit()
            return True
        return False

    def list_all(self, status: str = None, priority: str = None) -> list:
        query = self.db.query(ServiceOrder)

        if status:
            query = query.filter(ServiceOrder.status == ServiceOrderStatus(status))
        if priority:
            query = query.filter(ServiceOrder.priority == ServiceOrderPriority(priority))

        return query.order_by(ServiceOrder.created_at.desc()).all()
