from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from .validators import validate_spanish_tax_id

class CustomerBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    tax_id: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    country: str = Field(..., pattern=r'^[A-Z]{2}$')
    plan: str = Field(..., min_length=1, max_length=100)

    @field_validator('country')
    @classmethod
    def validate_country(cls, v):
        return v.upper()

    @field_validator('tax_id')
    @classmethod
    def validate_tax_id(cls, v, info):
        country = info.data.get('country', '').upper()
        if country == 'ES':
            is_valid, normalized = validate_spanish_tax_id(v)
            if not is_valid:
                raise ValueError('Invalid Spanish tax ID (NIF/NIE/CIF)')
            return normalized
        return v.strip().upper()

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SimulationBase(BaseModel):
    customer_id: int
    active_users: int = Field(..., ge=0)
    storage_gb: float = Field(..., ge=0)
    estimated_api_calls: int = Field(..., ge=0)

class SimulationCreate(SimulationBase):
    pass

class SimulationResponse(SimulationBase):
    id: int
    base_amount_cents: int
    tax_rate: float
    tax_amount_cents: int
    total_amount_cents: int
    created_at: datetime

    class Config:
        from_attributes = True

class SimulationPreview(BaseModel):
    active_users: int = Field(..., ge=0)
    storage_gb: float = Field(..., ge=0)
    estimated_api_calls: int = Field(..., ge=0)
    base_amount_cents: int
    tax_rate: float
    tax_amount_cents: int
    total_amount_cents: int
    currency: str = "EUR"
    exchange_rate: float = 1.0