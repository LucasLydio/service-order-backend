import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.infra.database.base import Base


class PasswordRecovery(Base):
    __tablename__ = "password_recovery"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    recovery_code = Column(String(6), nullable=False, unique=True)
    is_used = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<PasswordRecovery(id={self.id}, user_id={self.user_id})>"
