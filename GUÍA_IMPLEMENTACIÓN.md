# Guía Paso a Paso: Implementación de SaaS-O-Matic

## Resumen del Proyecto
SaaS-O-Matic es una aplicación full-stack para simulación y optimización de facturación SaaS con:
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Frontend**: React 18 + TypeScript + react-scripts
- **Validación**: NIF/NIE/CIF oficiales españoles
- **Precios**: Algoritmo por tramos escalonados
- **Multi-divisa**: Conversión en tiempo real vía API externa

---

## FASE 1: Preparación y Estructura Inicial

### 1.1 Análisis de Requisitos
Se leyó el archivo de requisitos (`Prueba Devs con IA.txt`) para identificar:
- Gestión de clientes (CRUD)
- Validación de identificación fiscal española
- Simulador de precios con tramos
- Persistencia de simulaciones
- Conversión de divisas
- API REST documentada

### 1.2 Creación de la estructura de carpetas
```
SaaS-O-Matic/
├── ai-workspace/           # Documentación de ingeniería
│   ├── 01-requirements/
│   ├── 02-architecture/
│   ├── 03-specifications/
│   ├── 04-ai-interactions/
│   └── 05-quality-assurance/
├── backend/
│   ├── app/
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── validators.py
│   │   └── pricing.py
│   ├── venv/
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   ├── services/
    │   ├── types/
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── App.css
    └── package.json
```

### 1.3 Configuración del entorno Python (Backend)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install fastapi uvicorn sqlalchemy pydantic python-multipart httpx pytest
pip freeze > requirements.txt
```

**requirements.txt final:**
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic[email]==2.5.0
python-multipart==0.0.6
httpx==0.25.2
pytest==7.4.3
```

---

## FASE 2: Backend - Capa de Datos y Modelos

### 2.1 Base de Datos (`backend/app/database.py`)
```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./saas.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Habilitar FK constraints en SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Puntos clave:**
- SQLite con foreign keys habilitadas
- Patrón dependency injection con `get_db()`
- `check_same_thread=False` para FastAPI

### 2.2 Modelos ORM (`backend/app/models.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    tax_id = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    country = Column(String(2), nullable=False)
    plan = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    simulations = relationship("Simulation", back_populates="customer", cascade="all, delete-orphan")

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
```

**Decisiones de diseño:**
- Precios en **céntimos** (enteros) para evitar problemas de precisión float
- Relación bidireccional con cascade delete
- Índices en `tax_id` y `customer_id` para búsquedas rápidas

---

## FASE 3: Backend - Validación de NIF/NIE/CIF

### 3.1 Algoritmos oficiales (`backend/app/validators.py`)

#### DNI (8 dígitos + letra control módulo 23)
```python
def _validate_dni(nif: str) -> bool:
    control_letters = "TRWAGMYFPDXBNJZSQVHLCKE"
    number = int(nif[:8])
    expected_letter = control_letters[number % 23]
    return nif[8] == expected_letter
```

#### NIE (X/Y/Z + 7 dígitos + letra)
```python
def _validate_nie(nie: str) -> bool:
    replacement = {'X': '0', 'Y': '1', 'Z': '2'}
    dni_like = replacement[nie[0]] + nie[1:]
    return _validate_dni(dni_like)
```

#### CIF (Letra + 7 dígitos + dígito/letra control)
```python
def _validate_cif(cif: str) -> bool:
    # Algoritmo: suma ponderada de posiciones pares/impares
    # Control = (10 - (suma % 10)) % 10
    # Puede ser dígito (0-9) o letra A-J (A=0...J=9)
```

**Validación principal:**
```python
def validate_spanish_tax_id(tax_id: str) -> Tuple[bool, str]:
    normalized = tax_id.upper().strip().replace(" ", "")
    
    dni_pattern = re.compile(r'^\d{8}[A-Z]$')
    nie_pattern = re.compile(r'^[XYZ]\d{7}[A-Z]$')
    cif_pattern = re.compile(r'^[ABCDEFGHJNPQRSUVW]\d{7}[\dA-J]$')
    
    if dni_pattern.match(normalized):
        return _validate_dni(normalized), normalized
    if nie_pattern.match(normalized):
        return _validate_nie(normalized), normalized
    if cif_pattern.match(normalized):
        return _validate_cif(normalized), normalized
    return False, normalized
```

---

## FASE 4: Backend - Esquemas Pydantic

### 4.1 Schemas (`backend/app/schemas.py`)
```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from .validators import validate_spanish_tax_id

class CustomerCreate(BaseModel):
    company_name: str
    tax_id: str
    email: EmailStr
    country: str
    plan: str
    
    @field_validator('tax_id')
    @classmethod
    def validate_tax_id(cls, v: str) -> str:
        is_valid, normalized = validate_spanish_tax_id(v)
        if not is_valid:
            raise ValueError('Invalid Spanish tax ID (NIF/NIE/CIF)')
        return normalized
    
    @field_validator('country')
    @classmethod
    def validate_country(cls, v: str) -> str:
        if len(v) != 2:
            raise ValueError('Country must be ISO 3166-1 alpha-2 code')
        return v.upper()

class CustomerResponse(CustomerCreate):
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
```

---

## FASE 5: Backend - Motor de Precios (Tiered Pricing)

### 5.1 Lógica de tramos (`backend/app/pricing.py`)
```python
# Tramos definidos por CAPACIDAD de cada tramo
TIERS = [
    {"count": 10, "price_per_user_cents": 1000},      # Usuarios 1-10: €10
    {"count": 40, "price_per_user_cents": 800},       # Usuarios 11-50: €8
    {"count": float('inf'), "price_per_user_cents": 500},  # Usuario 51+: €5
]

def calculate_base_price_cents(active_users: int) -> int:
    if active_users <= 0:
        return 0
    
    total_cents = 0
    remaining_users = active_users
    
    for tier in TIERS:
        users_in_tier = min(remaining_users, tier["count"])
        if users_in_tier <= 0:
            break
        total_cents += users_in_tier * tier["price_per_user_cents"]
        remaining_users -= users_in_tier
        if remaining_users <= 0:
            break
    
    return total_cents
```

**Ejemplos de cálculo:**
| Usuarios | Cálculo | Base (€) |
|----------|---------|----------|
| 1 | 1 × 1000 | 10.00 |
| 10 | 10 × 1000 | 100.00 |
| 11 | 10×1000 + 1×800 | 108.00 |
| 15 | 10×1000 + 5×800 | 140.00 |
| 50 | 10×1000 + 40×800 | 420.00 |
| 51 | 10×1000 + 40×800 + 1×500 | 425.00 |

### 5.2 Tasas de impuesto por país
```python
TAX_RATES = {
    "ES": 0.21, "DE": 0.19, "FR": 0.20, "IT": 0.22,
    "PT": 0.23, "NL": 0.21, "BE": 0.21, "AT": 0.20,
    "IE": 0.23, "FI": 0.24, "GR": 0.24, "PL": 0.23,
    "CZ": 0.21, "SE": 0.25, "DK": 0.25, "US": 0.0,
    "GB": 0.20, "CH": 0.081, "NO": 0.25,
}
DEFAULT_TAX_RATE = 0.0
```

---

## FASE 6: Backend - API REST (FastAPI)

### 6.1 Main (`backend/app/main.py`)
```python
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from .models import Customer, Simulation
from .schemas import (
    CustomerCreate, CustomerResponse,
    SimulationCreate, SimulationResponse, SimulationPreview
)
from .pricing import calculate_simulation_pricing

Base.metadata.create_all(bind=engine)
app = FastAPI(title="SaaS-O-Matic API", version="1.0.0")

# ===== HEALTH CHECK =====
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ===== CUSTOMERS =====
@app.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Verificar unicidad tax_id + country
    existing = db.query(Customer).filter(
        Customer.tax_id == customer.tax_id,
        Customer.country == customer.country
    ).first()
    if existing:
        raise HTTPException(400, "A customer with this tax ID already exists in this country")
    
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers", response_model=list[CustomerResponse])
def list_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()

@app.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    return customer

# ===== SIMULATIONS =====
@app.post("/simulations", response_model=SimulationResponse, status_code=201)
def create_simulation(sim: SimulationCreate, db: Session = Depends(get_db)):
    # Verificar cliente existe
    customer = db.query(Customer).filter(Customer.id == sim.customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    pricing = calculate_simulation_pricing(sim.active_users, customer.country)
    
    db_sim = Simulation(
        customer_id=sim.customer_id,
        active_users=sim.active_users,
        storage_gb=sim.storage_gb,
        estimated_api_calls=sim.estimated_api_calls,
        **pricing
    )
    db.add(db_sim)
    db.commit()
    db.refresh(db_sim)
    return db_sim

@app.post("/simulations/preview", response_model=SimulationPreview)
def preview_simulation(sim: SimulationCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == sim.customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    
    pricing = calculate_simulation_pricing(sim.active_users, customer.country)
    return SimulationPreview(
        active_users=sim.active_users,
        storage_gb=sim.storage_gb,
        estimated_api_calls=sim.estimated_api_calls,
        currency="EUR",
        exchange_rate=1.0,
        **pricing
    )

@app.get("/customers/{customer_id}/simulations", response_model=list[SimulationResponse])
def get_customer_simulations(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")
    return db.query(Simulation).filter(Simulation.customer_id == customer_id).all()

@app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    sim = db.query(Simulation).filter(Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(404, "Simulation not found")
    return sim
```

---

## FASE 7: Frontend - Configuración y Tipos

### 7.1 package.json (dependencias clave)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.7",
    "typescript": "^5.3.3",
    "ajv": "^8.12.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0"
  }
}
```

**Fixes aplicados:**
- `@types/react-dom@18.2.0` para compatibilidad React 18
- `ajv@8.12.0` para compatibilidad con react-scripts 5.0.1

### 7.2 tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "esnext",
    "moduleResolution": "bundler",
    "ignoreDeprecations": "6.0",
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "noEmit": true,
    "isolatedModules": true
  },
  "include": ["src"]
}
```

### 7.3 Tipos TypeScript (`frontend/src/types/index.ts`)
```typescript
export interface Customer {
  id: number;
  company_name: string;
  tax_id: string;
  email: string;
  country: string;
  plan: string;
  created_at: string;
}

export interface Simulation {
  id: number;
  customer_id: number;
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
  base_amount_cents: number;
  tax_rate: number;
  tax_amount_cents: number;
  total_amount_cents: number;
  created_at: string;
}

export interface SimulationPreview {
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
  base_amount_cents: number;
  tax_rate: number;
  tax_amount_cents: number;
  total_amount_cents: number;
  currency: string;
  exchange_rate: number;
}

export interface CreateCustomerData {
  company_name: string;
  tax_id: string;
  email: string;
  country: string;
  plan: string;
}

export interface CreateSimulationData {
  customer_id: number;
  active_users: number;
  storage_gb: number;
  estimated_api_calls: number;
}

export type ExchangeRates = Record<string, number>;
```

---

## FASE 8: Frontend - Servicios API

### 8.1 Cliente Axios (`frontend/src/services/api.ts`)
```typescript
import axios from 'axios';
import type { Customer, Simulation, CreateCustomerData, CreateSimulationData, SimulationPreview } from '../types';

const API_BASE_URL = 'http://localhost:8000';
const EXCHANGE_RATE_API = 'https://open.er-api.com/v6/latest/EUR';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const customerApi = {
  create: async (data: CreateCustomerData): Promise<Customer> => {
    const response = await api.post<Customer>('/customers', data);
    return response.data;
  },
  getAll: async (): Promise<Customer[]> => {
    const response = await api.get<Customer[]>('/customers');
    return response.data;
  },
  getById: async (id: number): Promise<Customer> => {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },
  search: async (query: string): Promise<Customer[]> => {
    const all = await customerApi.getAll();
    const lowerQuery = query.toLowerCase();
    return all.filter(c => 
      c.company_name.toLowerCase().includes(lowerQuery) ||
      c.tax_id.toLowerCase().includes(lowerQuery)
    );
  },
};

export const simulationApi = {
  create: async (data: CreateSimulationData): Promise<Simulation> => {
    const response = await api.post<Simulation>('/simulations', data);
    return response.data;
  },
  getByCustomer: async (customerId: number): Promise<Simulation[]> => {
    const response = await api.get<Simulation[]>(`/customers/${customerId}/simulations`);
    return response.data;
  },
  preview: async (customerId: number, activeUsers: number): Promise<SimulationPreview> => {
    const customer = await customerApi.getById(customerId);
    const response = await api.post<SimulationPreview>('/simulations/preview', {
      customer_id: customerId,
      active_users: activeUsers,
      storage_gb: 0,
      estimated_api_calls: 0,
    });
    return response.data;
  },
};

export const exchangeRateApi = {
  getRates: async (): Promise<Record<string, number>> => {
    try {
      const response = await axios.get(EXCHANGE_RATE_API);
      if (response.data.result === 'success') {
        return response.data.rates;
      }
      throw new Error('Failed to fetch exchange rates');
    } catch {
      // Fallback rates
      return { EUR: 1, USD: 1.08, GBP: 0.85, JPY: 160, CHF: 0.95, CAD: 1.48, AUD: 1.65 };
    }
  },
};

export const formatCurrency = (amountCents: number, currency: string, exchangeRates: Record<string, number>): string => {
  const rate = exchangeRates[currency] || 1;
  const amountEuros = amountCents / 100;
  const convertedAmount = amountEuros * rate;
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(convertedAmount);
};

export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('es-ES').format(num);
};
```

---

## FASE 9: Frontend - Componentes React

### 9.1 SimulationPreview (`frontend/src/components/SimulationPreview.tsx`)
**Características:**
- Slider interactivo para usuarios (0-200)
- Sliders para almacenamiento (0-1000 GB) y llamadas API (0-1M)
- Selector de divisa con tasas en tiempo real
- Cálculo en tiempo real via endpoint `/simulations/preview`
- Formato monetario localizado (es-ES)

```tsx
const SimulationPreviewComponent: React.FC<SimulationPreviewProps> = ({
  customerId, customerCountry, exchangeRates, selectedCurrency, onCurrencyChange
}) => {
  const [activeUsers, setActiveUsers] = useState(10);
  const [preview, setPreview] = useState<SimulationPreviewType | null>(null);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchPreview();
  }, [customerId, activeUsers]); // Solo recalcula al cambiar usuarios
  
  // ... render con sliders, select de divisa, resultados formateados
};
```

### 9.2 CustomerCard (`frontend/src/components/CustomerCard.tsx`)
**Características:**
- Tarjeta expandible con datos del cliente
- Badge de plan con colores (Basic=azul, Professional=purple, Enterprise=ámbar)
- Simulador integrado (SimulationPreview)
- Historial de simulaciones persistidas con toggle mostrar/ocultar
- Formulario para crear nuevas simulaciones

### 9.3 CustomerSearch (`frontend/src/components/CustomerSearch.tsx`)
**Características:**
- Header con título, selector de divisa global, botón nuevo cliente
- Formulario de creación de cliente (validación en frontend + backend)
- Buscador en tiempo real (filtro local por nombre o NIF/CIF)
- Grid responsive de CustomerCard
- Estados: loading, error, empty, results

---

## FASE 10: Frontend - App Principal y Estilos

### 10.1 App.tsx (`frontend/src/App.tsx`)
```tsx
const App: React.FC = () => {
  const [exchangeRates, setExchangeRates] = useState<ExchangeRates>({});
  const [selectedCurrency, setSelectedCurrency] = useState('EUR');
  const [loadingRates, setLoadingRates] = useState(true);

  useEffect(() => {
    const loadRates = async () => {
      try {
        const rates = await exchangeRateApi.getRates();
        setExchangeRates(rates);
      } catch (error) {
        console.error('Error loading exchange rates:', error);
      } finally {
        setLoadingRates(false);
      }
    };
    loadRates();
  }, []);

  if (loadingRates && Object.keys(exchangeRates).length === 0) {
    return <div className="app loading"><div className="spinner"></div><p>Cargando tipos de cambio...</p></div>;
  }

  return (
    <div className="app">
      <CustomerSearch
        exchangeRates={exchangeRates}
        selectedCurrency={selectedCurrency}
        onCurrencyChange={setSelectedCurrency}
      />
    </div>
  );
};
```

### 10.2 Estilos CSS (`frontend/src/App.css`)
**Sistema de diseño con CSS Variables:**
```css
:root {
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-success: #10b981;
  --color-error: #ef4444;
  --color-bg: #f8fafc;
  --color-card: #ffffff;
  --color-border: #e2e8f0;
  --color-text: #1e293b;
  --color-text-muted: #64748b;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.1);
  --transition: 0.2s ease;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f172a;
    --color-card: #1e293b;
    --color-border: #334155;
    --color-text: #f1f5f9;
    --color-text-muted: #94a3b8;
  }
}
```

**Componentes estilizados:**
- Grid responsive: `repeat(auto-fill, minmax(380px, 1fr))`
- Sliders personalizados con thumb azul
- Cards con hover elevation
- Badges de plan con colores semánticos
- Loading spinner animado
- Formularios con focus states accesibles

---

## FASE 11: Pruebas y Verificación

### 11.1 Verificación Backend
```bash
# Iniciar servidor
cd backend && .\venv\Scripts\python -m app.main

# Probar endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/customers -H "Content-Type: application/json" -d '{"company_name":"Test","tax_id":"B87654321","email":"test@test.com","country":"ES","plan":"professional"}'
curl -X POST http://localhost:8000/simulations/preview -H "Content-Type: application/json" -d '{"customer_id":1,"active_users":15,"storage_gb":100,"estimated_api_calls":10000}'
```

**Resultados esperados:**
- 15 usuarios → base_amount_cents: 14200 (€142) → con IVA 21% = €171.82
- Validación NIF: `12345678Z` ✓, `12345678A` ✗
- Validación CIF: `B87654321` ✓ (si dígito control correcto)

### 11.2 Verificación Frontend
```bash
cd frontend && npm start
# Abre http://localhost:3000
```

**Flujos a probar:**
1. Carga inicial → muestra spinner "Cargando tipos de cambio..."
2. Lista de clientes → busca por nombre o NIF
3. "+ Nuevo Cliente" → crea cliente con validación
4. Tarjeta cliente → slider usuarios → recalcula en tiempo real
5. Selector divisa → cambia EUR/USD/GBP → reformatea importes
6. "Ver simulaciones" → muestra historial + botón "Nueva Simulación"

---

## FASE 12: Problemas Comunes y Soluciones

| Problema | Causa | Solución |
|----------|-------|----------|
| `Module not found: react-dom/client` | Falta `@types/react-dom` | `npm install @types/react-dom@18.2.0` |
| `moduleResolution=node deprecated` | TSConfig obsoleto | Cambiar a `"moduleResolution": "bundler"` + `"ignoreDeprecations": "6.0"` |
| `ajv` error con react-scripts | Versión incompatible | `npm install ajv@8.12.0` |
| Puerto 8000 ocupado | Proceso anterior | `taskkill /F /IM python.exe` |
| CIF `B87654321` falla | Dígito control incorrecto | Verificar algoritmo CIF en validators.py |
| DNI `12345678A` falla | Letra control incorrecta | Verificar módulo 23: 12345678 % 23 = ? |

---

## FASE 13: Documentación Final

### 13.1 README.md completo con:
- Arquitectura del sistema
- Inicio rápido (backend + frontend)
- Referencia API completa
- Ejemplo de cálculo de precios
- Validación NIF/NIE/CIF
- Estructura de carpetas
- Criterios de evaluación cubiertos

### 13.2 Documentación en `ai-workspace/`
```
01-requirements/     # Especificaciones funcionales
02-architecture/     # Diagramas y decisiones técnicas
03-specifications/   # Contratos API, schemas DB
04-ai-interactions/  # Prompts y contexto de desarrollo
05-quality-assurance/ # Plan de pruebas, checklists
```

---

## COMANDOS DE REFERENCIA RÁPIDA

```bash
# BACKEND
cd backend
.\venv\Scripts\activate
python -m app.main                    # Servidor dev
uvicorn app.main:app --reload         # Con auto-reload
python -m pytest                        # Tests

# FRONTEND
cd frontend
npm install                           # Instalar deps
npm start                             # Dev server (puerto 3000)
npm run build                         # Build producción
npm test                              # Tests

# LIMPIEZA
# Backend: eliminar saas.db para resetear BD
# Frontend: eliminar node_modules + package-lock.json + npm install
```

---

## ARQUITECTURA FINAL

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Customer    │  │ Customer    │  │ SimulationPreview   │  │
│  │ Search      │──│ Card        │──│ (Sliders + Preview) │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────┘  │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────┐                                    │
│  │   Services/API      │  ◄── Axios + Exchange Rate API    │
│  └──────────┬──────────┘                                    │
└─────────────│───────────────────────────────────────────────┘
              │ HTTP/JSON
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Customers   │  │ Simulations │  │ Pricing Engine      │  │
│  │ Router      │  │ Router      │  │ (Tiered + Tax)      │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         ▼                ▼                     ▼             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLAlchemy + SQLite                    │    │
│  │  Customers ◄────── Simulations (FK, Cascade)        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## CHECKLIST DE ENTREGA ✅

- [x] Backend FastAPI funcional en puerto 8000
- [x] Frontend React funcional en puerto 3000
- [x] CRUD Clientes con validación NIF/NIE/CIF
- [x] Simulador precios tramos (0-10: €10, 11-50: €8, 51+: €5)
- [x] Impuestos por país (IVA UE, US sin IVA, etc.)
- [x] Persistencia simulaciones en SQLite
- [x] Preview tiempo real sin persistir
- [x] Conversión divisas API externa + fallback
- [x] UI responsive: búsqueda, tarjetas, sliders, historial
- [x] Selector divisa global + por simulador
- [x] Manejo errores: loading, empty, error states
- [x] Documentación README completa
- [x] Código limpio, tipado estricto, sin warnings ESLint

---

*Guía generada como referencia completa del proceso de implementación de SaaS-O-Matic.*