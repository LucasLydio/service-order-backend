from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceOrderCreateSchema(BaseModel):
    equipment: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(default="MEDIA")


class ServiceOrderUpdateSchema(BaseModel):
    equipment: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    cancellation_reason: Optional[str] = None
    priority: Optional[str] = None


class ServiceOrderAssignSchema(BaseModel):
    technician_id: str


class ServiceOrderResponseSchema(BaseModel):
    id: str
    customer_id: str
    technician_id: Optional[str] = None
    equipment: str
    description: Optional[str] = None
    cancellation_reason: Optional[str] = None
    status: str
    priority: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
