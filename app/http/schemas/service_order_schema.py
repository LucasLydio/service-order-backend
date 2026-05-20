from pydantic import BaseModel
from datetime import datetime


class ServiceOrderCreateSchema(BaseModel):
    title: str
    description: str = None


class ServiceOrderUpdateSchema(BaseModel):
    title: str = None
    description: str = None
    status: str = None


class ServiceOrderResponseSchema(BaseModel):
    id: str
    customer_id: str
    title: str
    description: str = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
