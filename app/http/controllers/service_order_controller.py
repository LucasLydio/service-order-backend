import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.http.schemas.service_order_schema import (
    ServiceOrderCreateSchema, ServiceOrderUpdateSchema, ServiceOrderAddPartSchema
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
    return success_response("Ordem de serviço criada com sucesso", {"id": order.id})


@router.get("/", response_model=StandardResponse)
def list_service_orders(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = ServiceOrderService(db)
    orders = service.list_service_orders()
    data = [
        {
            "id": o.id,
            "customer_id": o.customer_id,
            "title": o.title,
            "description": o.description,
            "status": getattr(o.status, "value", str(o.status)),
            "created_at": o.created_at,
            "updated_at": o.updated_at,
        }
        for o in orders
    ]
    return success_response("Ordens de serviço listadas com sucesso", data)


@router.get("/{order_id}", response_model=StandardResponse)
def get_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician", "client")),
):
    service = ServiceOrderService(db)
    order = service.get_service_order(str(order_id))
    data = {
        "id": order.id,
        "customer_id": order.customer_id,
        "title": order.title,
        "description": order.description,
        "status": getattr(order.status, "value", str(order.status)),
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }
    return success_response("Ordem de serviço encontrada", data)


@router.put("/{order_id}", response_model=StandardResponse)
def update_service_order(
    order_id: uuid.UUID,
    data: ServiceOrderUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = ServiceOrderService(db)
    order = service.update_service_order(str(order_id), **data.dict(exclude_unset=True))
    return success_response("Ordem de serviço atualizada com sucesso", {"id": order.id})


@router.post("/{order_id}/parts", response_model=StandardResponse)
def add_part_to_order(
    order_id: uuid.UUID,
    data: ServiceOrderAddPartSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = ServiceOrderService(db)
    service.add_part_to_order(str(order_id), data.part_id, data.quantity)
    return success_response("Peça vinculada à ordem de serviço com sucesso")


@router.get("/{order_id}/history", response_model=StandardResponse)
def get_order_history(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = ServiceOrderService(db)
    history = service.get_order_history(str(order_id))
    data = [
        {
            "id": h.id,
            "event_type": h.event_type,
            "description": h.description,
            "service_order_id": h.service_order_id,
            "part_id": h.part_id,
            "created_at": h.created_at,
        }
        for h in history
    ]
    return success_response("Histórico da OS recuperado com sucesso", data)


@router.delete("/{order_id}", response_model=StandardResponse)
def delete_service_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = ServiceOrderService(db)
    service.delete_service_order(str(order_id))
    return success_response("Ordem de serviço removida com sucesso")