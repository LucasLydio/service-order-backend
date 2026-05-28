import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.http.schemas.service_order_schema import (
    ServiceOrderCreateSchema, ServiceOrderUpdateSchema, ServiceOrderResponseSchema
)
from app.http.services.service_order_service import ServiceOrderService
from app.http.middlewares.role_middleware import require_roles
from app.infra.database.session import get_db
from app.shared.responses import success_response, StandardResponse

router = APIRouter()


@router.post("/", response_model=StandardResponse)
def create_service_order(
    customer_id: uuid.UUID,
    data: ServiceOrderCreateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.create_service_order(str(customer_id), data.title, data.description)
    return success_response("Service order created", {"id": order.id})


@router.get("/{order_id}", response_model=StandardResponse)
def get_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "client")),
):
    service = ServiceOrderService(db)
    order = service.get_service_order(str(order_id))
    if not order:
        return success_response("Service order retrieved", None)

    data = {
        "id": order.id,
        "customer_id": order.customer_id,
        "title": order.title,
        "description": order.description,
        "status": getattr(order.status, "value", str(order.status)),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }
    return success_response("Service order retrieved", data)


@router.put("/{order_id}", response_model=StandardResponse)
def update_service_order(
    order_id: uuid.UUID,
    data: ServiceOrderUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.update_service_order(str(order_id), **data.dict(exclude_unset=True))
    return success_response("Service order updated", {"id": order.id})


@router.delete("/{order_id}", response_model=StandardResponse)
def delete_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = ServiceOrderService(db)
    service.delete_service_order(str(order_id))
    return success_response("Service order deleted")
