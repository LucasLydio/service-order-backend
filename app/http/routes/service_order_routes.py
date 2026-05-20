from fastapi import APIRouter
from app.http.controllers import service_order_controller

router = APIRouter(prefix="/service-orders", tags=["service-orders"])
router.include_router(service_order_controller.router)
