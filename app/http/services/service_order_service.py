from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.infra.repositories.service_order_repository import ServiceOrderRepository
from app.infra.models.service_order_model import ServiceOrderStatus, ServiceOrderPriority
from app.shared.exceptions import (
    ServiceOrderNotFoundException,
    CompletedOrderNotEditableException,
    OrderWithoutTechnicianException,
)


class ServiceOrderService:
    def __init__(self, db: Session):
        self.repo = ServiceOrderRepository(db)
        self.db = db

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

    def create_service_order(self, customer_id: str, title: str, description: str = None, priority: str = "MEDIA"):
        self._validate_priority(priority)
        return self.repo.create(
            customer_id=customer_id,
            title=title,
            description=description,
            priority=priority,
        )

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

        current_status = order.status
        if isinstance(current_status, ServiceOrderStatus):
            current_status = current_status.value
        if current_status == ServiceOrderStatus.COMPLETED.value:
            raise CompletedOrderNotEditableException()

        if "priority" in kwargs and kwargs["priority"] is not None:
            self._validate_priority(kwargs["priority"])
        if "status" in kwargs and kwargs["status"] is not None:
            self._validate_status(kwargs["status"])

            if kwargs["status"] == ServiceOrderStatus.COMPLETED.value:
                if not order.technician_id:
                    raise OrderWithoutTechnicianException()

        return self.repo.update(order_id, **kwargs)

    def assign_technician(self, order_id: str, technician_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        current_status = order.status
        if isinstance(current_status, ServiceOrderStatus):
            current_status = current_status.value
        if current_status == ServiceOrderStatus.COMPLETED.value:
            raise CompletedOrderNotEditableException()

        return self.repo.assign_technician(order_id, technician_id)

    def complete_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        if not order.technician_id:
            raise OrderWithoutTechnicianException()

        current_status = order.status
        if isinstance(current_status, ServiceOrderStatus):
            current_status = current_status.value
        if current_status == ServiceOrderStatus.COMPLETED.value:
            raise CompletedOrderNotEditableException()

        return self.repo.update(order_id, status=ServiceOrderStatus.COMPLETED.value)

    def delete_service_order(self, order_id: str):
        order = self.repo.find_by_id(order_id)
        if not order:
            raise ServiceOrderNotFoundException()

        current_status = order.status
        if isinstance(current_status, ServiceOrderStatus):
            current_status = current_status.value
        if current_status == ServiceOrderStatus.COMPLETED.value:
            raise CompletedOrderNotEditableException()

        self.repo.delete(order_id)
        return True

    def list_service_orders(self, status_filter: str = None, priority_filter: str = None):
        if status_filter:
            self._validate_status(status_filter)
        if priority_filter:
            self._validate_priority(priority_filter)
        return self.repo.list_all(status=status_filter, priority=priority_filter)
