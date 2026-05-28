from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


class PartCreateSchema(BaseModel):
    name: str
    sku: str
    quantity: int
    price: float
    description: Optional[str] = None

    @field_validator("quantity")
    def quantity_nao_pode_ser_negativo(cls, v):
        if v < 0:
            raise ValueError("A quantidade não pode ser negativa")
        return v

    @field_validator("price")
    def preco_nao_pode_ser_negativo(cls, v):
        if v < 0:
            raise ValueError("O preço não pode ser negativo")
        return v


class PartUpdateSchema(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    description: Optional[str] = None

    @field_validator("quantity")
    def quantity_nao_pode_ser_negativo(cls, v):
        if v is not None and v < 0:
            raise ValueError("A quantidade não pode ser negativa")
        return v

    @field_validator("price")
    def preco_nao_pode_ser_negativo(cls, v):
        if v is not None and v < 0:
            raise ValueError("O preço não pode ser negativo")
        return v


class PartResponseSchema(BaseModel):
    id: str
    name: str
    sku: str
    quantity: int
    price: float
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True