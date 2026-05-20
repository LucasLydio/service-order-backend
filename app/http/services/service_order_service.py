from sqlalchemy.orm import Session
from app.infra.repositories.service_order_repository import ServiceOrderRepository
from app.shared.exceptions import UserNotFoundException


class ServiceOrderService:
    def __init__(self, db: Session):
        self.repo = ServiceOrderRepository(db)
        self.db = db

    def create_service_order(self, customer_id: str, title: str, description: str = None):
        return self.repo.create(customer_id=customer_id, title=title, description=description)

    def get_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()
        return order

    def get_orders_by_customer(self, customer_id: str):
        return self.repo.find_by_customer_id(customer_id)

    def update_service_order(self, order_id: str, **kwargs):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()
        return self.repo.update(order_id, **kwargs)

    def delete_service_order(self, order_id: str):
        success = self.repo.delete(order_id)
        if not success:
            raise UserNotFoundException()
        return True

    def list_service_orders(self):
        return self.repo.list_all()
