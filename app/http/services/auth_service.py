from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.infra.repositories.user_repository import UserRepository
from app.infra.repositories.password_recovery_repository import PasswordRecoveryRepository
from app.shared.security import hash_password, verify_password, create_access_token
from app.shared.exceptions import InvalidCredentialsException, UserAlreadyExistsException, UserNotFoundException
import random
import string


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.recovery_repo = PasswordRecoveryRepository(db)
        self.db = db

    def register(self, email: str, password: str, full_name: str = None):
        existing_user = self.user_repo.find_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException()

        hashed_password = hash_password(password)
        user = self.user_repo.create(
            email=email,
            password=hashed_password,
            full_name=full_name,
            role="client"
        )
        return user

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)
        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        token = create_access_token({
            "sub": user.id,
            "email": user.email,
            "role": user.role
        })
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            },
            "access_token": token,
            "token_type": "bearer"
        }

    def request_password_recovery(self, email: str):
        user = self.user_repo.find_by_email(email)
        if not user:
            return {"message": "If email exists, recovery code was sent"}

        code = "".join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(hours=1)
        self.recovery_repo.create(user_id=user.id, code=code, expires_at=expires_at)

        return {"message": "Recovery code sent to email"}

    def confirm_password_recovery(self, email: str, code: str, new_password: str):
        user = self.user_repo.find_by_email(email)
        if not user:
            raise InvalidCredentialsException()

        recovery = self.recovery_repo.find_by_code(code)
        if not recovery or recovery.user_id != user.id or recovery.is_used:
            raise InvalidCredentialsException()

        if recovery.expires_at < datetime.utcnow():
            raise InvalidCredentialsException()

        hashed_password = hash_password(new_password)
        self.user_repo.update(user.id, password=hashed_password)
        self.recovery_repo.mark_as_used(code)

        return {"message": "Password updated successfully"}

    def get_user(self, user_id: str):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        return user

