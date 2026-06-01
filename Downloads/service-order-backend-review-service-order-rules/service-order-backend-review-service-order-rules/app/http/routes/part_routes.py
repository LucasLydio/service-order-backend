from fastapi import APIRouter
from app.http.controllers import part_controller

router = APIRouter(prefix="/parts", tags=["parts"])
router.include_router(part_controller.router)