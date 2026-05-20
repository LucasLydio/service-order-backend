from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.http.schemas.auth_schema import (
    UserRegisterSchema, UserLoginSchema, TokenSchema,
    PasswordRecoveryRequestSchema, PasswordRecoveryConfirmSchema, UserResponseSchema
)
from app.http.services.auth_service import AuthService
from app.http.middlewares.auth_middleware import verify_token
from app.infra.database.session import get_db
from app.shared.responses import success_response

router = APIRouter()


@router.post("/register", response_model=dict)
def register(data: UserRegisterSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(data.email, data.password, data.full_name)
    return success_response("User registered successfully", {"id": user.id, "email": user.email})


@router.post("/login", response_model=dict)
def login(data: UserLoginSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.login(data.email, data.password)
    return success_response("Login successful", result)


@router.post("/password-recovery/request", response_model=dict)
def request_password_recovery(data: PasswordRecoveryRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.request_password_recovery(data.email)
    return success_response(result["message"])


@router.post("/password-recovery/confirm", response_model=dict)
def confirm_password_recovery(data: PasswordRecoveryConfirmSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    result = service.confirm_password_recovery(data.email, data.code, data.new_password)
    return success_response(result["message"])


@router.get("/me", response_model=dict)
def me(current_user: dict = Depends(verify_token), db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.get_user(current_user["sub"])
    return success_response(
        "User retrieved",
        {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role},
    )
