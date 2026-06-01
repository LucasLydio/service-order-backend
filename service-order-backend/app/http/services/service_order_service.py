from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.infra.models.order_part_model import OrderPart
from app.infra.models.service_order_model import ServiceOrderPriority, ServiceOrderStatus
from app.infra.repositories.history_repository import HistoryRepository
from app.infra.repositories.part_repository import PartRepository
from app.infra.repositories.service_order_repository import ServiceOrderRepository
from app.shared.exceptions import (
    CancellationReasonRequiredException,
    CompletedOrderNotEditableException,
    InsufficientStockException,
    OrderWithoutTechnicianException,
    PartNotFoundException,
    ServiceOrderNotFoundException,
    TechnicianOrderLimitExceededException,
)


class ServiceOrderService:
    def __init__(self, db: Session):
        self.repo = ServiceOrderRepository(db)
        self.parts = PartRepository(db)
        self.history = HistoryRepository(db)
        self.db = db

    def _normalize_status(self, value):
        if isinstance(value, ServiceOrderStatus):
            return value.value
        return value

    def _is_finalized(self, order) -> bool:
        status_value = self._normalize_status(order.status)
        return status_value in {ServiceOrderStatus.COMPLETED.value, ServiceOrderStatus.CANCELLED.value}

    def _validate_priority(self, priority: str):
        allowed = [p.value for p in ServiceOrderPriority]
        if priority and priority not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority. Allowed values: {', '.join(allowed)}"
            )

    def _validate_status(self, status_value: str):
        allowed = [s.value for s in ServiceOrderStatus]
        if status_value and status_value not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Allowed values: {', '.join(allowed)}"
            )

    def _record_history(self, event_type: str, description: str, service_order_id: str, part_id: str = None):
        self.history.create(
            event_type=event_type,
            description=description,
            service_order_id=service_order_id,
            part_id=part_id,
        )

    def _ensure_technician_capacity(self, technician_id: str, order_id: str = None):
        active_orders = self.repo.count_active_by_technician(technician_id, exclude_order_id=order_id)
        if active_orders >= 5:
            raise TechnicianOrderLimitExceededException()

    def _calculate_service_time_seconds(self, order, finished_at: datetime) -> int:
        created_at = order.created_at or finished_at
        return max(0, int((finished_at - created_at).total_seconds()))

    def create_service_order(self, customer_id: str, title: str, description: str = None, priority: str = "MEDIA"):
        self._validate_priority(priority)
        order = self.repo.create(
            customer_id=customer_id,
            title=title,
            description=description,
            priority=priority,
        )
        self._record_history(
            event_type="ORDER_CREATED",
            description=f"Service order '{order.title}' created with status {self._normalize_status(order.status)}",
            service_order_id=order.id,
        )
        return order

    def get_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()
        return order

    def get_orders_by_customer(self, customer_id: str):
        return self.repo.find_by_customer_id(customer_id)

    def update_service_order(self, order_id: str, **kwargs):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        if "priority" in kwargs and kwargs["priority"] is not None:
            self._validate_priority(kwargs["priority"])

        old_status = self._normalize_status(order.status)
        new_status = kwargs.get("status")

        if new_status is not None:
            self._validate_status(new_status)

            if new_status == ServiceOrderStatus.COMPLETED.value and not order.technician_id:
                raise OrderWithoutTechnicianException()

            if new_status == ServiceOrderStatus.IN_PROGRESS.value and not order.technician_id:
                raise OrderWithoutTechnicianException()

            if new_status == ServiceOrderStatus.CANCELLED.value:
                cancellation_reason = kwargs.get("cancellation_reason")
                if not cancellation_reason:
                    raise CancellationReasonRequiredException()
                finished_at = datetime.now(timezone.utc)
                kwargs["cancellation_reason"] = cancellation_reason
                kwargs["completed_at"] = finished_at
                kwargs["service_time_seconds"] = self._calculate_service_time_seconds(order, finished_at)

            if new_status == ServiceOrderStatus.COMPLETED.value:
                finished_at = datetime.now(timezone.utc)
                kwargs["completed_at"] = finished_at
                kwargs["service_time_seconds"] = self._calculate_service_time_seconds(order, finished_at)

        updated = self.repo.update(order_id, **kwargs)

        if new_status is not None and self._normalize_status(updated.status) != old_status:
            self._record_history(
                event_type="ORDER_STATUS_CHANGED",
                description=f"Order status changed from {old_status} to {self._normalize_status(updated.status)}",
                service_order_id=updated.id,
            )

        return updated

    def assign_technician(self, order_id: str, technician_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        self._ensure_technician_capacity(technician_id, order_id=order.id)

        updated = self.repo.assign_technician(order_id, technician_id)
        self._record_history(
            event_type="ORDER_ASSIGNED",
            description=f"Technician {technician_id} assigned and order moved to IN_PROGRESS",
            service_order_id=updated.id,
        )
        return updated

    def complete_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if not order.technician_id:
            raise OrderWithoutTechnicianException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        finished_at = datetime.now(timezone.utc)
        updated = self.repo.update(
            order_id,
            status=ServiceOrderStatus.COMPLETED.value,
            completed_at=finished_at,
            service_time_seconds=self._calculate_service_time_seconds(order, finished_at),
        )
        self._record_history(
            event_type="ORDER_COMPLETED",
            description="Service order completed",
            service_order_id=updated.id,
        )
        return updated

    def cancel_service_order(self, order_id: str, reason: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        if not reason:
            raise CancellationReasonRequiredException()

        finished_at = datetime.now(timezone.utc)
        updated = self.repo.update(
            order_id,
            status=ServiceOrderStatus.CANCELLED.value,
            cancellation_reason=reason,
            completed_at=finished_at,
            service_time_seconds=self._calculate_service_time_seconds(order, finished_at),
        )
        self._record_history(
            event_type="ORDER_CANCELLED",
            description=f"Service order cancelled: {reason}",
            service_order_id=updated.id,
        )
        return updated

    def list_order_history(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()
        return self.history.find_by_service_order(order_id)

    def use_part_on_order(self, order_id: str, part_id: str, quantity: int):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        part = self.parts.find_by_id(part_id)
        if not part:
            raise PartNotFoundException()
        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity must be greater than zero")
        if quantity > part.quantity:
            raise InsufficientStockException(part.name)

        order_part = OrderPart(service_order_id=order_id, part_id=part_id, quantity=quantity)
        part.quantity -= quantity
        self.db.add(order_part)
        self.db.commit()
        self.db.refresh(order_part)
        self.db.refresh(part)
        self._record_history(
            event_type="ORDER_PART_USED",
            description=f"Part '{part.name}' used in order {order_id} with quantity {quantity}",
            service_order_id=order_id,
            part_id=part_id,
        )
        return {
            "order_part_id": order_part.id,
            "service_order_id": order_part.service_order_id,
            "part_id": order_part.part_id,
            "quantity": order_part.quantity,
            "remaining_stock": part.quantity,
        }

    def delete_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if self._is_finalized(order):
            raise CompletedOrderNotEditableException()

        self.repo.delete(order_id)
        return True

    def list_service_orders(self, status_filter: str = None, priority_filter: str = None):
        if status_filter:
            self._validate_status(status_filter)
        if priority_filter:
            self._validate_priority(priority_filter)
        return self.repo.list_all(status=status_filter, priority=priority_filter)
