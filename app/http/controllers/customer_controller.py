import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.http.schemas.customer_schema import (
    CustomerCreateSchema, CustomerUpdateSchema, CustomerResponseSchema
)
from app.http.services.customer_service import CustomerService
from app.http.middlewares.role_middleware import require_roles
from app.infra.database.session import get_db
from app.shared.responses import success_response

router = APIRouter()


@router.post("/", response_model=dict)
def create_customer(
    data: CustomerCreateSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "manager")),
):
    user_id = current_user["sub"]
    service = CustomerService(db)
    customer = service.create_customer(user_id, **data.dict(exclude_unset=True))
    return success_response("Customer created", {"id": customer.id})


@router.get("/{customer_id}", response_model=dict)
def get_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customer = service.get_customer(str(customer_id))
    return success_response("Customer retrieved", customer.__dict__)


@router.put("/{customer_id}", response_model=dict)
def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = CustomerService(db)
    customer = service.update_customer(str(customer_id), **data.dict(exclude_unset=True))
    return success_response("Customer updated", {"id": customer.id})


@router.delete("/{customer_id}", response_model=dict)
def delete_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = CustomerService(db)
    service.delete_customer(str(customer_id))
    return success_response("Customer deleted")
