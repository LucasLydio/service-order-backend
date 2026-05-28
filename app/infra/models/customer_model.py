import uuid

from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.infra.database.base import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(255), nullable=False, index=True)
    cpf = Column(String(20), nullable=False, unique=True, index=True)
    telefone = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    endereco = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Customer(id={self.id}, nome={self.nome}, cpf={self.cpf})>"
