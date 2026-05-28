from fastapi import APIRouter
from app.http.controllers import auth_controller

router = APIRouter(prefix="/auth", tags=["auth"])
router.include_router(auth_controller.router)
