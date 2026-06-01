from sqlalchemy.orm import Session
from app.infra.models.history_model import History


class HistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, event_type: str, description: str, service_order_id: str = None, part_id: str = None) -> History:
        record = History(
            event_type=event_type,
            description=description,
            service_order_id=service_order_id,
            part_id=part_id
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list:
        return self.db.query(History).all()

    def find_by_service_order(self, service_order_id: str) -> list:
        return self.db.query(History).filter(History.service_order_id == service_order_id).all()