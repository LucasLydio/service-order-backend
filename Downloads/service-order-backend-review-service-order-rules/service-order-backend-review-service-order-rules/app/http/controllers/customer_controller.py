import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.http.schemas.customer_schema import (
    CustomerCreateSchema, CustomerUpdateSchema, CustomerResponseSchema
)
from app.http.services.customer_service import CustomerService
from app.http.middlewares.role_middleware import require_roles
from app.infra.database.session import get_db
from app.shared.responses import success_response, StandardResponse

router = APIRouter()


def _serialize_customer(customer):
    return CustomerResponseSchema.model_validate(customer).model_dump()


@router.post("/", response_model=StandardResponse)
def create_customer(
    data: CustomerCreateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customer = service.create_customer(**data.model_dump())
    return success_response("Customer created", _serialize_customer(customer))


@router.get("/", response_model=StandardResponse)
def list_customers(
    nome: Optional[str] = Query(default=None),
    cpf: Optional[str] = Query(default=None),
    email: Optional[str] = Query(default=None),
    telefone: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customers = service.list_customers(nome=nome, cpf=cpf, email=email, telefone=telefone)
    return success_response("Customers retrieved", [_serialize_customer(customer) for customer in customers])


@router.get("/{customer_id}", response_model=StandardResponse)
def get_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customer = service.get_customer(str(customer_id))
    return success_response("Customer retrieved", _serialize_customer(customer))


@router.put("/{customer_id}", response_model=StandardResponse)
def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customer = service.update_customer(str(customer_id), **data.model_dump(exclude_unset=True))
    return success_response("Customer updated", _serialize_customer(customer))


@router.delete("/{customer_id}", response_model=StandardResponse)
def delete_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = CustomerService(db)
    service.delete_customer(str(customer_id))
    return success_response("Customer deleted")
