from fastapi import Depends
from sqlalchemy.orm import Session

from app.infra.database.session import get_db
from app.infra.repositories.reports_repository import ReportsRepository
from app.shared.responses import StandardResponse, success_response


def get_average_service_time(db: Session = Depends(get_db)) -> StandardResponse:
    repo = ReportsRepository(db)
    return success_response(
        "Average service time report generated",
        repo.get_average_service_time(),
    )


def get_most_used_parts(db: Session = Depends(get_db)) -> StandardResponse:
    repo = ReportsRepository(db)
    return success_response(
        "Most used parts report generated",
        repo.get_most_used_parts(),
    )


def get_orders_by_technician(db: Session = Depends(get_db)) -> StandardResponse:
    repo = ReportsRepository(db)
    return success_response(
        "Orders by technician report generated",
        repo.get_service_orders_by_technician(),
    )


def get_orders_by_status(db: Session = Depends(get_db)) -> StandardResponse:
    repo = ReportsRepository(db)
    return success_response(
        "Orders by status report generated",
        repo.get_service_orders_by_status(),
    )


def get_late_orders(db: Session = Depends(get_db)) -> StandardResponse:
    repo = ReportsRepository(db)
    return success_response(
        "Late orders report generated",
        repo.get_late_orders(),
    )
