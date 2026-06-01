import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.http.schemas.part_schema import PartCreateSchema, PartUpdateSchema
from app.http.services.part_service import PartService
from app.http.middlewares.role_middleware import require_roles
from app.infra.database.session import get_db
from app.shared.responses import success_response, StandardResponse

router = APIRouter()


@router.post("/", response_model=StandardResponse)
def create_part(
    data: PartCreateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = PartService(db)
    part = service.create_part(
        name=data.name,
        sku=data.sku,
        quantity=data.quantity,
        price=data.price,
        description=data.description
    )
    return success_response("Peça cadastrada com sucesso", {"id": part.id})


@router.get("/", response_model=StandardResponse)
def list_parts(
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = PartService(db)
    parts = service.list_parts()
    data = [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "quantity": p.quantity,
            "price": float(p.price),
            "description": p.description,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
        }
        for p in parts
    ]
    return success_response("Peças listadas com sucesso", data)


@router.get("/{part_id}", response_model=StandardResponse)
def get_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager", "technician")),
):
    service = PartService(db)
    part = service.get_part(str(part_id))
    data = {
        "id": part.id,
        "name": part.name,
        "sku": part.sku,
        "quantity": part.quantity,
        "price": float(part.price),
        "description": part.description,
        "created_at": part.created_at,
        "updated_at": part.updated_at,
    }
    return success_response("Peça encontrada", data)


@router.put("/{part_id}", response_model=StandardResponse)
def update_part(
    part_id: uuid.UUID,
    data: PartUpdateSchema,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin", "manager")),
):
    service = PartService(db)
    part = service.update_part(str(part_id), **data.dict(exclude_unset=True))
    return success_response("Peça atualizada com sucesso", {"id": part.id})


@router.delete("/{part_id}", response_model=StandardResponse)
def delete_part(
    part_id: uuid.UUID,
    db: Session = Depends(get_db),
    _current_user: dict = Depends(require_roles("admin")),
):
    service = PartService(db)
    service.delete_part(str(part_id))
    return success_response("Peça removida com sucesso")