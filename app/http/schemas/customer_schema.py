from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class CustomerCreateSchema(BaseModel):
    nome: str = Field(..., min_length=2, max_length=255)
    cpf: str = Field(..., min_length=11, max_length=20)
    telefone: str = Field(..., min_length=8, max_length=20)
    email: EmailStr
    endereco: str = Field(..., min_length=5, max_length=255)


class CustomerUpdateSchema(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=255)
    cpf: Optional[str] = Field(default=None, min_length=11, max_length=20)
    telefone: Optional[str] = Field(default=None, min_length=8, max_length=20)
    email: Optional[EmailStr] = None
    endereco: Optional[str] = Field(default=None, min_length=5, max_length=255)


class CustomerResponseSchema(BaseModel):
    id: str
    nome: str
    cpf: str
    telefone: str
    email: str
    endereco: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
