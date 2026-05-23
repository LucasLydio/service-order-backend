from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from app.infra.models.customer_model import Customer
from app.infra.models.service_order_model import ServiceOrder


class CustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, customer_id: str) -> Customer:
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def find_by_cpf(self, cpf: str) -> Customer:
        return self.db.query(Customer).filter(Customer.cpf == cpf).first()

    def find_by_email(self, email: str) -> Customer:
        return self.db.query(Customer).filter(Customer.email == email).first()

    def create(self, **kwargs) -> Customer:
        customer = Customer(**kwargs)
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
            # remove dependent service orders first to avoid FK constraint
            self.db.query(ServiceOrder).filter(ServiceOrder.customer_id == customer_id).delete(synchronize_session=False)
            self.db.delete(customer)
            self.db.commit()
            return True
        return False

    def list_all(self, nome: str = None, cpf: str = None, email: str = None, telefone: str = None) -> list:
        query = self.db.query(Customer)

        filters = []
        if nome:
            filters.append(func.lower(Customer.nome).like(f"%{nome.lower()}%"))
        if cpf:
            filters.append(func.lower(Customer.cpf).like(f"%{cpf.lower()}%"))
        if email:
            filters.append(func.lower(Customer.email).like(f"%{email.lower()}%"))
        if telefone:
            filters.append(func.lower(Customer.telefone).like(f"%{telefone.lower()}%"))

        if filters:
            query = query.filter(or_(*filters))

        return query.order_by(Customer.nome.asc()).all()
