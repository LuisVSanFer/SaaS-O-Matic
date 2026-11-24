from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    tax_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    country = Column(String, nullable=False)
    plan = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    simulations = relationship("Simulation", back_populates="customer")

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    active_users = Column(Integer, nullable=False)
    storage_gb = Column(Float, nullable=False)
    estimated_api_calls = Column(Integer, nullable=False)
    base_amount_cents = Column(Integer, nullable=False)
    tax_rate = Column(Float, nullable=False)
    tax_amount_cents = Column(Integer, nullable=False)
    total_amount_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="simulations")
