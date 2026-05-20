from sqlalchemy.orm import Session
from app.infra.models.customer_model import Customer


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, customer_id: str) -> Customer:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def find_by_user_id(self, user_id: str) -> Customer:
        return self.db.query(Customer).filter(Customer.user_id == user_id).first()

    def create(self, user_id: str, **kwargs) -> Customer:
        customer = Customer(user_id=user_id, **kwargs)
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def update(self, customer_id: str, **kwargs) -> Customer:
        customer = self.find_by_id(customer_id)
        for key, value in kwargs.items():
            setattr(customer, key, value)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def delete(self, customer_id: str) -> bool:
        customer = self.find_by_id(customer_id)
        if customer:
            self.db.delete(customer)
            self.db.commit()
            return True
        return False

    def list_all(self) -> list:
        return self.db.query(Customer).all()
