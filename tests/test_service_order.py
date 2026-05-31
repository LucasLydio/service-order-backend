import pytest
from unittest.mock import Mock

from app.http.services.service_order_service import ServiceOrderService
from app.shared.exceptions import (
    OrderWithoutTechnicianException,
    CompletedOrderNotEditableException,
)


def test_complete_order_without_technician():

    db = Mock()

    service = ServiceOrderService(db)

    order = Mock()
    order.id = "123"
    order.technician_id = None
    order.status = "PENDING"

    service.repo.find_by_id = Mock(return_value=order)

    with pytest.raises(OrderWithoutTechnicianException):
        service.complete_service_order("123")


def test_completed_order_cannot_be_edited():

    db = Mock()

    service = ServiceOrderService(db)

    order = Mock()
    order.id = "123"
    order.status = "COMPLETED"

    service.repo.find_by_id = Mock(return_value=order)

    with pytest.raises(CompletedOrderNotEditableException):
        service.update_service_order(
            "123",
            title="Novo Titulo"
        )