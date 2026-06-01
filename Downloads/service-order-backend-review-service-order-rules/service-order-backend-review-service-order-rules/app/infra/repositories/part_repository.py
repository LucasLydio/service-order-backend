from sqlalchemy.orm import Session
from app.infra.models.part_model import Part


class PartRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, part_id: str) -> Part:
        return self.db.query(Part).filter(Part.id == part_id).first()

    def find_by_sku(self, sku: str) -> Part:
        return self.db.query(Part).filter(Part.sku == sku).first()

    def list_all(self) -> list:
        return self.db.query(Part).all()

    def create(self, name: str, sku: str, quantity: int, price: float, description: str = None) -> Part:
        part = Part(name=name, sku=sku, quantity=quantity, price=price, description=description)
        self.db.add(part)
        self.db.commit()
        self.db.refresh(part)
        return part

    def update(self, part_id: str, **kwargs) -> Part:
        part = self.find_by_id(part_id)
        for key, value in kwargs.items():
            setattr(part, key, value)
        self.db.commit()
        self.db.refresh(part)
        return part

    def delete(self, part_id: str) -> bool:
        part = self.find_by_id(part_id)
        if part:
            self.db.delete(part)
            self.db.commit()
            return True
        return False