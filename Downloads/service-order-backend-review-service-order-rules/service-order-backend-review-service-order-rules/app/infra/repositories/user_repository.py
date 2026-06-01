from sqlalchemy.orm import Session
from app.infra.models.user_model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def find_by_id(self, user_id: str) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, email: str, password: str, full_name: str = None, role: str = "client") -> User:
        user = User(email=email, password=password, full_name=full_name, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user_id: str, **kwargs) -> User:
        user = self.find_by_id(user_id)
        for key, value in kwargs.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        user = self.find_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
