from sqlalchemy.orm import Session
from app.infra.repositories.part_repository import PartRepository
from app.infra.repositories.history_repository import HistoryRepository
from app.shared.exceptions import PartNotFoundException, InsufficientStockException


class PartService:
    def __init__(self, db: Session):
        self.repo = PartRepository(db)
        self.history = HistoryRepository(db)

    def create_part(self, name: str, sku: str, quantity: int, price: float, description: str = None):
        part = self.repo.create(
            name=name,
            sku=sku,
            quantity=quantity,
            price=price,
            description=description
        )
        self.history.create(
            event_type="PART_CREATED",
            description=f"Peça '{part.name}' (SKU: {part.sku}) cadastrada com {part.quantity} unidades em estoque",
            part_id=part.id
        )
        return part

    def get_part(self, part_id: str):
        part = self.repo.find_by_id(part_id)
        if not part:
            raise PartNotFoundException()
        return part

    def list_parts(self):
        return self.repo.list_all()

    def update_part(self, part_id: str, **kwargs):
        part = self.repo.find_by_id(part_id)
        if not part:
            raise PartNotFoundException()
        updated = self.repo.update(part_id, **kwargs)
        self.history.create(
            event_type="PART_UPDATED",
            description=f"Peça '{updated.name}' (SKU: {updated.sku}) foi atualizada",
            part_id=updated.id
        )
        return updated

    def delete_part(self, part_id: str):
        part = self.repo.find_by_id(part_id)
        if not part:
            raise PartNotFoundException()
        self.history.create(
            event_type="PART_DELETED",
            description=f"Peça '{part.name}' (SKU: {part.sku}) foi removida do sistema",
            part_id=part.id
        )
        self.repo.delete(part_id)
        return True

    def use_part(self, part_id: str, quantity_used: int):
        part = self.repo.find_by_id(part_id)
        if not part:
            raise PartNotFoundException()
        if quantity_used > part.quantity:
            raise InsufficientStockException(part.name)
        updated = self.repo.update(part_id, quantity=part.quantity - quantity_used)
        self.history.create(
            event_type="PART_USED",
            description=f"Peça '{part.name}' (SKU: {part.sku}) teve {quantity_used} unidade(s) utilizada(s). Estoque restante: {updated.quantity}",
            part_id=part.id
        )
        return updated