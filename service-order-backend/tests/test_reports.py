from datetime import datetime, timedelta
from unittest.mock import Mock

from app.infra.repositories.reports_repository import ReportsRepository


def test_average_service_time_report_calculates_completed_orders():
    first_order = Mock()
    first_order.created_at = datetime(2026, 5, 31, 8, 0, 0)
    first_order.updated_at = datetime(2026, 5, 31, 10, 0, 0)

    second_order = Mock()
    second_order.created_at = datetime(2026, 5, 31, 9, 0, 0)
    second_order.updated_at = second_order.created_at + timedelta(hours=4)

    query = Mock()
    query.filter.return_value = query
    query.all.return_value = [first_order, second_order]

    db = Mock()
    db.query.return_value = query

    report = ReportsRepository(db).get_average_service_time()

    assert report == {
        "completed_orders": 2,
        "average_seconds": 10800.0,
        "average_hours": 3.0,
    }
