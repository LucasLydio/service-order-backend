from fastapi import APIRouter
from app.http.controllers import customer_controller

router = APIRouter(prefix="/customers", tags=["customers"])
router.include_router(customer_controller.router)
