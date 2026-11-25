from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from .validators import validate_spanish_tax_id


class CustomerBase(BaseModel):
    company_name: str
    tax_id: str
    email: EmailStr
    country: str
    plan: str


class CustomerCreate(CustomerBase):
    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        cleaned = v.strip().upper()
        if len(cleaned) != 2:
            raise ValueError("Country must be an ISO 3166-1 alpha-2 code (e.g., ES, US)")
        return cleaned

    @field_validator("tax_id")
    @classmethod
    def normalize_tax_id(cls, v: str) -> str:
        return v.upper().strip().replace(" ", "")

    @model_validator(mode="after")
    def validate_tax_id_for_country(self) -> "CustomerCreate":
        # Cross-field validation runs after both country and tax_id are populated
        if self.country == "ES":
            is_valid, normalized = validate_spanish_tax_id(self.tax_id)
            if not is_valid:
                raise ValueError("Invalid Spanish tax ID (DNI/NIE/CIF)")
            self.tax_id = normalized
        return self


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class SimulationCreate(BaseModel):
    customer_id: int
    active_users: int
    storage_gb: float
    estimated_api_calls: int


class SimulationResponse(SimulationCreate):
    id: int
    base_amount_cents: int
    tax_rate: float
    tax_amount_cents: int
    total_amount_cents: int
    created_at: datetime

    class Config:
        from_attributes = True


class SimulationPreview(BaseModel):
    active_users: int
    storage_gb: float
    estimated_api_calls: int
    base_amount_cents: int
    tax_rate: float
    tax_amount_cents: int
    total_amount_cents: int
    currency: str
    exchange_rate: float