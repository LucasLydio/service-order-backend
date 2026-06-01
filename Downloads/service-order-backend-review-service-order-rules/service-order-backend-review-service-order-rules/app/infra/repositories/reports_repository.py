from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime

from app.infra.models.order_part_model import OrderPart
from app.infra.models.part_model import Part
from app.infra.models.service_order_model import ServiceOrder, ServiceOrderStatus
from app.infra.models.technician_model import Technician
from datetime import timedelta


class ReportsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_average_service_time(self) -> dict:
        completed_orders = (
            self.db.query(ServiceOrder)
            .filter(ServiceOrder.status == ServiceOrderStatus.COMPLETED)
            .all()
        )

        def _safe_seconds(order) -> float:
            service_time_seconds = getattr(order, "service_time_seconds", None)
            if isinstance(service_time_seconds, (int, float)):
                return float(service_time_seconds)

            completed_at = getattr(order, "completed_at", None)
            created_at = getattr(order, "created_at", None)
            updated_at = getattr(order, "updated_at", None)

            if isinstance(completed_at, datetime) and isinstance(created_at, datetime):
                return float((completed_at - created_at).total_seconds())
            if isinstance(updated_at, datetime) and isinstance(created_at, datetime):
                return float((updated_at - created_at).total_seconds())
            return 0.0

        durations = [_safe_seconds(order) for order in completed_orders]

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

    def get_overdue_service_orders(self, days: int = 7) -> list[dict]:
        """Return service orders in IN_PROGRESS older than `days` days."""
        now = datetime.utcnow()
        threshold = now - timedelta(days=days)

        result = (
            self.db.query(ServiceOrder)
            .filter(ServiceOrder.status == ServiceOrderStatus.IN_PROGRESS)
            .filter(ServiceOrder.created_at < threshold)
            .all()
        )

        overdue = []
        for order in result:
            created_at = getattr(order, "created_at", None)
            age_days = None
            if isinstance(created_at, datetime):
                age_days = int((now - created_at).days)

            overdue.append(
                {
                    "id": order.id,
                    "title": getattr(order, "title", None),
                    "customer_id": getattr(order, "customer_id", None),
                    "technician_id": getattr(order, "technician_id", None),
                    "status": getattr(order.status, "value", str(order.status)) if order.status else None,
                    "priority": getattr(order.priority, "value", str(order.priority)) if order.priority else None,
                    "created_at": created_at.isoformat() if getattr(created_at, "isoformat", None) else None,
                    "age_days": age_days,
                }
            )

        return overdue
