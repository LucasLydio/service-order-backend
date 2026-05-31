from fastapi import APIRouter
from app.http.controllers.reports_controller import (
    get_average_service_time,
    get_most_used_parts,
    get_orders_by_status,
    get_orders_by_technician,
)

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

router.add_api_route(
    "/average-service-time",
    get_average_service_time,
    methods=["GET"]
)

router.add_api_route(
    "/most-used-parts",
    get_most_used_parts,
    methods=["GET"]
)

router.add_api_route(
    "/orders-by-technician",
    get_orders_by_technician,
    methods=["GET"]
)

router.add_api_route(
    "/orders-by-status",
    get_orders_by_status,
    methods=["GET"]
)
