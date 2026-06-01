from sqlalchemy.orm import Session
from app.infra.models.password_recovery_model import PasswordRecovery


class PasswordRecoveryRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_code(self, code: str) -> PasswordRecovery:
        return self.db.query(PasswordRecovery).filter(
            PasswordRecovery.recovery_code == code
        ).first()

    def find_by_user_id(self, user_id: str) -> PasswordRecovery:
        return self.db.query(PasswordRecovery).filter(
            PasswordRecovery.user_id == user_id
        ).first()

    def create(self, user_id: str, code: str, expires_at) -> PasswordRecovery:
        recovery = PasswordRecovery(user_id=user_id, recovery_code=code, expires_at=expires_at)
        self.db.add(recovery)
        self.db.commit()
        self.db.refresh(recovery)
        return recovery

    def mark_as_used(self, code: str) -> bool:
        recovery = self.find_by_code(code)
        if recovery:
            recovery.is_used = 1
            self.db.commit()
            return True
        return False
