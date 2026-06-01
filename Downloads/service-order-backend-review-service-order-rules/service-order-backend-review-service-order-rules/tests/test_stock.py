import pytest
from unittest.mock import Mock

from app.http.services.part_service import PartService
from app.shared.exceptions import InsufficientStockException


def test_stock_cannot_be_negative_when_using_part():
    db = Mock()
    service = PartService(db)

    part = Mock()
    part.id = "part-123"
    part.name = "Tela LCD"
    part.quantity = 2

    service.repo.find_by_id = Mock(return_value=part)
    service.repo.update = Mock()
    service.history.create = Mock()

    with pytest.raises(InsufficientStockException):
        service.use_part("part-123", 3)

    service.repo.update.assert_not_called()
    service.history.create.assert_not_called()
