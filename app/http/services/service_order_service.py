from sqlalchemy.orm import Session
from app.infra.repositories.service_order_repository import ServiceOrderRepository
from app.infra.repositories.history_repository import HistoryRepository
from app.infra.repositories.part_repository import PartRepository
from app.infra.models.order_part_model import OrderPart
from app.infra.models.service_order_model import ServiceOrderStatus
from app.http.services.part_service import PartService
from app.shared.exceptions import (
    UserNotFoundException,
    TechnicianOrderLimitException,
    CancellationReasonRequiredException
)


class ServiceOrderService:
    def __init__(self, db: Session):
        self.repo = ServiceOrderRepository(db)
        self.history = HistoryRepository(db)
        self.part_repo = PartRepository(db)
        self.part_service = PartService(db)
        self.db = db

    def create_service_order(self, customer_id: str, title: str, description: str = None):
        order = self.repo.create(customer_id=customer_id, title=title, description=description)
        self.history.create(
            event_type="OS_CREATED",
            description=f"Ordem de serviço '{title}' criada para o cliente {customer_id}",
            service_order_id=order.id
        )
        return order

    def get_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()
        return order

    def get_orders_by_customer(self, customer_id: str):
        return self.repo.find_by_customer_id(customer_id)

    def update_service_order(self, order_id: str, **kwargs):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()

        new_status = kwargs.get("status")
        cancellation_reason = kwargs.get("cancellation_reason")
        technician_id = kwargs.get("technician_id")

        # Regra: OS concluída não pode ser editada
        if order.status == ServiceOrderStatus.COMPLETED:
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="Ordens de serviço concluídas não podem ser editadas")

        # Regra: cancelamento exige motivo
        if new_status == "CANCELLED" and not cancellation_reason:
            raise CancellationReasonRequiredException()

        # Regra: técnico não pode ter mais de 5 OS em andamento
        if technician_id:
            orders_in_progress = self.db.query(self.repo.db.query.__self__.__class__).filter_by(
                technician_id=technician_id,
                status=ServiceOrderStatus.IN_PROGRESS
            ).count() if False else self._count_technician_orders(technician_id)
            if orders_in_progress >= 5:
                raise TechnicianOrderLimitException()

        updated = self.repo.update(order_id, **kwargs)

        # Registra no histórico se o status mudou
        if new_status and new_status != str(order.status.value):
            description = f"Status da OS alterado para '{new_status}'"
            if new_status == "CANCELLED" and cancellation_reason:
                description += f". Motivo: {cancellation_reason}"
            self.history.create(
                event_type="STATUS_CHANGED",
                description=description,
                service_order_id=order_id
            )

        return updated

    def _count_technician_orders(self, technician_id: str) -> int:
        from app.infra.models.service_order_model import ServiceOrder
        return self.db.query(ServiceOrder).filter(
            ServiceOrder.technician_id == technician_id,
            ServiceOrder.status == ServiceOrderStatus.IN_PROGRESS
        ).count()

    def add_part_to_order(self, order_id: str, part_id: str, quantity: int):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()

        # Regra: OS concluída ou cancelada não pode receber peças
        if order.status in [ServiceOrderStatus.COMPLETED, ServiceOrderStatus.CANCELLED]:
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="Não é possível adicionar peças a uma OS concluída ou cancelada")

        # Desconta do estoque e registra no histórico de peças
        part = self.part_service.use_part(part_id, quantity)

        # Vincula a peça à OS
        order_part = OrderPart(
            service_order_id=order_id,
            part_id=part_id,
            quantity=quantity
        )
        self.db.add(order_part)
        self.db.commit()

        # Registra no histórico da OS
        self.history.create(
            event_type="PART_USED",
            description=f"Peça '{part.name}' (SKU: {part.sku}) — {quantity} unidade(s) vinculada(s) à OS",
            service_order_id=order_id,
            part_id=part_id
        )

        return order_part

    def get_order_history(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise UserNotFoundException()
        return self.history.find_by_service_order(order_id)

    def delete_service_order(self, order_id: str):
        success = self.repo.delete(order_id)
        if not success:
            raise UserNotFoundException()
        return True

    def list_service_orders(self):
        return self.repo.list_all()