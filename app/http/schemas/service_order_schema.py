from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ServiceOrderCreateSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = Field(default="MEDIA")


class ServiceOrderUpdateSchema(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)


class ServiceOrderAssignSchema(BaseModel):
    technician_id: str


class ServiceOrderCancelSchema(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class ServiceOrderPartUseSchema(BaseModel):
    quantity: int = Field(..., ge=1)


class ServiceOrderResponseSchema(BaseModel):
    id: str
    customer_id: str
    technician_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    completed_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    service_time_seconds: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
