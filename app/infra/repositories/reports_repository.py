from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.infra.models.order_part_model import OrderPart
from app.infra.models.part_model import Part
from app.infra.models.service_order_model import ServiceOrder, ServiceOrderStatus
from app.infra.models.technician_model import Technician


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_average_service_time(self) -> dict:
        completed_orders = (
            self.db.query(ServiceOrder)
            .filter(ServiceOrder.status == ServiceOrderStatus.COMPLETED)
            .filter(ServiceOrder.updated_at.isnot(None))
            .all()
        )

        durations = [
            (order.updated_at - order.created_at).total_seconds()
            for order in completed_orders
            if order.created_at and order.updated_at
        ]

        average_seconds = sum(durations) / len(durations) if durations else 0
        return {
            "completed_orders": len(durations),
            "average_seconds": round(average_seconds, 2),
            "average_hours": round(average_seconds / 3600, 2),
        }

    def get_most_used_parts(self) -> list[dict]:
        result = (
            self.db.query(
                Part.name.label("part_name"),
                func.sum(OrderPart.quantity).label("quantity_used"),
            )
            .join(OrderPart, Part.id == OrderPart.part_id)
            .group_by(Part.id, Part.name)
            .order_by(func.sum(OrderPart.quantity).desc())
            .all()
        )

        return [
            {
                "part_name": row.part_name,
                "quantity_used": int(row.quantity_used or 0),
            }
            for row in result
        ]

    def get_service_orders_by_technician(self) -> list[dict]:
        result = (
            self.db.query(
                Technician.full_name.label("technician"),
                func.count(ServiceOrder.id).label("total_orders"),
            )
            .join(ServiceOrder, Technician.id == ServiceOrder.technician_id)
            .group_by(Technician.id, Technician.full_name)
            .order_by(func.count(ServiceOrder.id).desc())
            .all()
        )

        return [
            {
                "technician": row.technician,
                "total_orders": int(row.total_orders or 0),
            }
            for row in result
        ]

    def get_service_orders_by_status(self) -> list[dict]:
        result = (
            self.db.query(
                ServiceOrder.status.label("status"),
                func.count(ServiceOrder.id).label("total_orders"),
            )
            .group_by(ServiceOrder.status)
            .order_by(func.count(ServiceOrder.id).desc())
            .all()
        )

        return [
            {
                "status": getattr(row.status, "value", str(row.status)),
                "total_orders": int(row.total_orders or 0),
            }
            for row in result
        ]

    def get_late_orders(self) -> list[dict]:
        threshold = datetime.now(timezone.utc) - timedelta(days=5)
        result = (
            self.db.query(ServiceOrder)
            .filter(ServiceOrder.status.in_([ServiceOrderStatus.PENDING, ServiceOrderStatus.IN_PROGRESS]))
            .filter(ServiceOrder.created_at < threshold)
            .all()
        )
        return [
            {
                "id": str(order.id),
                "equipment": order.equipment,
                "status": getattr(order.status, "value", str(order.status)),
                "created_at": order.created_at.isoformat() if order.created_at else None,
            }
            for order in result
        ]
