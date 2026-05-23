from sqlalchemy.orm import Session
from app.infra.repositories.customer_repository import CustomerRepository
from app.shared.exceptions import CustomerNotFoundException


class CustomerService:
    def __init__(self, db: Session):
        self.repo = CustomerRepository(db)
        self.db = db

    def create_customer(self, **kwargs):
        return self.repo.create(**kwargs)

    def get_customer(self, customer_id: str):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException()
        return customer

    def update_customer(self, customer_id: str, **kwargs):
        customer = self.repo.find_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundException()
        return self.repo.update(customer_id, **kwargs)

    def delete_customer(self, customer_id: str):
        success = self.repo.delete(customer_id)
        if not success:
            raise CustomerNotFoundException()
        return True

    def list_customers(self, nome: str = None, cpf: str = None, email: str = None, telefone: str = None):
        return self.repo.list_all(nome=nome, cpf=cpf, email=email, telefone=telefone)
