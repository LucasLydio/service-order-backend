from pydantic import BaseModel
from datetime import datetime


class CustomerCreateSchema(BaseModel):
    phone: str = None
    address: str = None
    city: str = None
    state: str = None


class CustomerUpdateSchema(BaseModel):
    phone: str = None
    address: str = None
    city: str = None
    state: str = None


class CustomerResponseSchema(BaseModel):
    id: str
    user_id: str
    phone: str = None
    address: str = None
    city: str = None
    state: str = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
