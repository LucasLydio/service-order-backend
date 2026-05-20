from sqlalchemy.orm import Session
from app.infra.repositories.customer_repository import CustomerRepository
from app.shared.exceptions import UserNotFoundException


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.db = db

    def create_customer(self, user_id: str, **kwargs):
        return self.repo.create(user_id=user_id, **kwargs)

    def get_customer(self, customer_id: str):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise UserNotFoundException()
        return customer

    def get_customer_by_user(self, user_id: str):
        customer = self.repo.find_by_user_id(user_id)
        if not customer:
            raise UserNotFoundException()
        return customer

    def update_customer(self, customer_id: str, **kwargs):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise UserNotFoundException()
        return self.repo.update(customer_id, **kwargs)

    def delete_customer(self, customer_id: str):
        success = self.repo.delete(customer_id)
        if not success:
            raise UserNotFoundException()
        return True

    def list_customers(self):
        return self.repo.list_all()
