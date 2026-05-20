from sqlalchemy.orm import Session
from app.infra.models.service_order_model import ServiceOrder


class ServiceOrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, order_id: str) -> ServiceOrder:
        return self.db.query(ServiceOrder).filter(ServiceOrder.id == order_id).first()

    def find_by_customer_id(self, customer_id: str) -> list:
        return self.db.query(ServiceOrder).filter(ServiceOrder.customer_id == customer_id).all()

    def create(self, customer_id: str, title: str, description: str = None) -> ServiceOrder:
        order = ServiceOrder(customer_id=customer_id, title=title, description=description)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: str, **kwargs) -> ServiceOrder:
        order = self.find_by_id(order_id)
        for key, value in kwargs.items():
            setattr(order, key, value)
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

    def list_all(self) -> list:
        return self.db.query(ServiceOrder).all()
