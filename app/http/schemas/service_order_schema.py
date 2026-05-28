from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ServiceOrderCreateSchema(BaseModel):
    title: str
    description: Optional[str] = None


class ServiceOrderUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    technician_id: Optional[str] = None
    cancellation_reason: Optional[str] = None


class ServiceOrderAddPartSchema(BaseModel):
    part_id: str
    quantity: int


class ServiceOrderResponseSchema(BaseModel):
    id: str
    customer_id: str
    title: str
    description: Optional[str] = None
    status: str
    technician_id: Optional[str] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True