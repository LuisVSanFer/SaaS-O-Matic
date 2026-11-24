from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .database import engine, get_db
from .models import Customer, Simulation
from .schemas import CustomerCreate, CustomerResponse, SimulationCreate, SimulationResponse, SimulationPreview
from .pricing import calculate_simulation_pricing

# Create tables
from .models import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SaaS-O-Matic API",
    description="Dynamic Billing & Subscription Optimizer for SaaS",
    version="1.0.0"
)




@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Check if customer with same tax_id and country already exists
    existing = db.query(Customer).filter(
        Customer.tax_id == customer.tax_id,
        Customer.country == customer.country
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this tax ID already exists in this country"
        )

    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers", response_model=List[CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Customer).offset(skip).limit(limit).all()

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/simulations", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    # Verify customer exists
    customer = db.query(Customer).filter(Customer.id == simulation.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Calculate pricing
    pricing = calculate_simulation_pricing(simulation.active_users, customer.country)

    # Create simulation with calculated pricing
    db_simulation = Simulation(
        customer_id=simulation.customer_id,
        active_users=simulation.active_users,
        storage_gb=simulation.storage_gb,
        estimated_api_calls=simulation.estimated_api_calls,
        **pricing
    )

    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation

@app.get("/customers/{customer_id}/simulations", response_model=List[SimulationResponse])
def get_customer_simulations(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return db.query(Simulation).filter(Simulation.customer_id == customer_id).all()

@app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return simulation

@app.post("/simulations/preview", response_model=SimulationPreview)
def preview_simulation(simulation: SimulationCreate, db: Session = Depends(get_db)):
    """Preview simulation pricing without persisting"""
    customer = db.query(Customer).filter(Customer.id == simulation.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    pricing = calculate_simulation_pricing(simulation.active_users, customer.country)

    return SimulationPreview(
        active_users=simulation.active_users,
        storage_gb=simulation.storage_gb,
        estimated_api_calls=simulation.estimated_api_calls,
        currency="EUR",
        exchange_rate=1.0,
        **pricing
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)