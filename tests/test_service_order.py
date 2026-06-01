import pytest
from unittest.mock import Mock

from app.http.services.service_order_service import ServiceOrderService
from app.shared.exceptions import (
    OrderWithoutTechnicianException,
    CompletedOrderNotEditableException,
    TechnicianOrderLimitExceededException,
    CancellationReasonRequiredException,
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


def test_technician_cannot_receive_more_than_five_active_orders():

    db = Mock()

    service = ServiceOrderService(db)

    order = Mock()
    order.id = "123"
    order.status = "PENDING"

    service.repo.find_by_id = Mock(return_value=order)
    service.repo.count_active_by_technician = Mock(return_value=5)

    with pytest.raises(TechnicianOrderLimitExceededException):
        service.assign_technician("123", "tech-1")


def test_cancel_order_requires_reason():

    db = Mock()

    service = ServiceOrderService(db)

    order = Mock()
    order.id = "123"
    order.status = "PENDING"

    service.repo.find_by_id = Mock(return_value=order)

    with pytest.raises(CancellationReasonRequiredException):
        service.cancel_service_order("123", "")