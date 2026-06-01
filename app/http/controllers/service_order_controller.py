import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.http.schemas.service_order_schema import (
    ServiceOrderCreateSchema,
    ServiceOrderUpdateSchema,
    ServiceOrderAssignSchema,
    ServiceOrderCancelSchema,
    ServiceOrderPartUseSchema,
    ServiceOrderResponseSchema,
)
from app.http.services.service_order_service import ServiceOrderService
from app.http.middlewares.role_middleware import require_roles
from app.infra.database.session import get_db
from app.shared.responses import success_response, StandardResponse

router = APIRouter()


def _serialize_order(order):
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "technician_id": order.technician_id,
        "title": order.title,
        "description": order.description,
        "status": getattr(order.status, "value", str(order.status)),
        "priority": getattr(order.priority, "value", str(order.priority)),
        "completed_at": getattr(order, "completed_at", None),
        "cancellation_reason": getattr(order, "cancellation_reason", None),
        "service_time_seconds": getattr(order, "service_time_seconds", None),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


def _serialize_history_item(item):
    return {
        "id": item.id,
        "event_type": item.event_type,
        "description": item.description,
        "service_order_id": item.service_order_id,
        "part_id": item.part_id,
        "created_at": item.created_at,
    }


@router.post("/", response_model=StandardResponse)
def create_service_order(
    customer_id: uuid.UUID,
    data: ServiceOrderCreateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.create_service_order(
        str(customer_id), data.title, data.description, data.priority
    )
    return success_response("Service order created", _serialize_order(order))


@router.get("/", response_model=StandardResponse)
def list_service_orders(
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "client")),
):
    service = ServiceOrderService(db)
    orders = service.list_service_orders(status_filter=status, priority_filter=priority)
    return success_response(
        "Service orders retrieved",
        [_serialize_order(o) for o in orders],
    )


@router.get("/{order_id}", response_model=StandardResponse)
def get_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "client")),
):
    service = ServiceOrderService(db)
    order = service.get_service_order(str(order_id))
    return success_response("Service order retrieved", _serialize_order(order))


@router.get("/customer/{customer_id}", response_model=StandardResponse)
def get_orders_by_customer(
    customer_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "client")),
):
    service = ServiceOrderService(db)
    orders = service.get_orders_by_customer(str(customer_id))
    return success_response(
        "Customer orders retrieved",
        [_serialize_order(o) for o in orders],
    )


@router.put("/{order_id}", response_model=StandardResponse)
def update_service_order(
    order_id: uuid.UUID,
    data: ServiceOrderUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.update_service_order(str(order_id), **data.model_dump(exclude_unset=True))
    return success_response("Service order updated", _serialize_order(order))


@router.patch("/{order_id}/cancel", response_model=StandardResponse)
def cancel_service_order(
    order_id: uuid.UUID,
    data: ServiceOrderCancelSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.cancel_service_order(str(order_id), data.reason)
    return success_response("Service order cancelled", _serialize_order(order))


@router.patch("/{order_id}/assign", response_model=StandardResponse)
def assign_technician(
    order_id: uuid.UUID,
    data: ServiceOrderAssignSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.assign_technician(str(order_id), data.technician_id)
    return success_response("Technician assigned to service order", _serialize_order(order))


@router.patch("/{order_id}/complete", response_model=StandardResponse)
def complete_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.complete_service_order(str(order_id))
    return success_response("Service order completed", _serialize_order(order))


@router.post("/{order_id}/parts/{part_id}", response_model=StandardResponse)
def use_part_on_order(
    order_id: uuid.UUID,
    part_id: uuid.UUID,
    data: ServiceOrderPartUseSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = ServiceOrderService(db)
    result = service.use_part_on_order(str(order_id), str(part_id), data.quantity)
    return success_response("Part applied to service order", result)


@router.get("/{order_id}/history", response_model=StandardResponse)
def list_order_history(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = ServiceOrderService(db)
    history = service.list_order_history(str(order_id))
    return success_response("Order history retrieved", [_serialize_history_item(item) for item in history])


@router.delete("/{order_id}", response_model=StandardResponse)
def delete_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = ServiceOrderService(db)
    service.delete_service_order(str(order_id))
    return success_response("Service order deleted")
