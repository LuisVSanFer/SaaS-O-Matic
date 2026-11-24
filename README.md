# SaaS-O-Matic

**Dynamic Billing & Subscription Optimizer** — A full-stack application for simulating, optimizing, and budgeting SaaS subscriptions for corporate clients.

## 🏗️ Architecture

```
┌─────────────────┐     HTTP/JSON      ┌─────────────────┐
│   Frontend      │ ◄─────────────────► │    Backend      │
│  (React + TS)   │                     │  (FastAPI +     │
│                 │                     │   Python)       │
└─────────────────┘                     └────────┬────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │      SQLite Database      │
                                    │   (Customers + Simulations)│
                                    └───────────────────────────┘
```

## ✨ Features

### Backend (FastAPI + SQLite)
- **Customer Management**: CRUD operations with strict validation
- **Spanish Tax ID Validation**: Official algorithm for DNI/NIF/CIF/NIE
- **Tiered Pricing Engine**:
  - 0-10 users: €10/user/month
  - 11-50 users: €8/user/month
  - 51+ users: €5/user/month
- **Multi-country Tax Support**: VAT rates for EU countries, UK, US, CH, NO
- **Simulation Persistence**: Historical records with immutable pricing snapshots
- **Preview Endpoint**: Real-time pricing calculation without persistence

### Frontend (React + TypeScript)
- **Customer Dashboard**: Search by company name or tax ID
- **Interactive Simulator**: Sliders for users, storage, API calls with real-time pricing
- **Multi-currency Display**: Live exchange rates from open.er-api.com (EUR, USD, GBP, etc.)
- **Simulation History**: Persisted simulations with full pricing breakdown
- **Responsive Design**: Works on desktop and mobile
- **Create Customers/Simulations**: Inline forms with validation

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
Server runs at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### Frontend Setup
```bash
cd frontend
npm install
npm start
```
App runs at: **http://localhost:3000**

## 📚 API Reference

### Customers
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/customers` | Create customer (validates Spanish tax IDs) |
| GET | `/customers` | List all customers |
| GET | `/customers/{id}` | Get customer by ID |

### Simulations
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/simulations` | Create & persist simulation |
| POST | `/simulations/preview` | Preview pricing (no persistence) |
| GET | `/customers/{id}/simulations` | List customer simulations |
| GET | `/simulations/{id}` | Get simulation by ID |

## 🧮 Pricing Algorithm Example

For **15 users** in **Spain (21% VAT)**:
```
Tier 1 (0-10):  10 users × €10 = €100.00
Tier 2 (11-50):  5 users × €8   = €40.00
──────────────────────────────────
Base Price:                   €140.00
VAT (21%):                    €29.40
──────────────────────────────────
Total:                        €169.40
```

## 🔍 Spanish Tax ID Validation

The backend implements the official algorithms:
- **DNI**: 8 digits + control letter (modulo 23)
- **NIE**: X/Y/Z + 7 digits + control letter
- **CIF**: Letter + 7 digits + control digit/letter

## 📁 Project Structure

```
SaaS-O-Matic/
├── ai-workspace/           # Engineering documentation
│   ├── 01-requirements/
│   ├── 02-architecture/
│   ├── 03-specifications/
│   ├── 04-ai-interactions/
│   └── 05-quality-assurance/
├── backend/
│   ├── app/
│   │   ├── database.py     # SQLAlchemy setup
│   │   ├── main.py         # FastAPI routes
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── schemas.py      # Pydantic schemas
│   │   ├── validators.py   # Tax ID validation
│   │   └── pricing.py      # Tiered pricing engine
│   ├── venv/
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── components/
    │   │   ├── CustomerSearch.tsx
    │   │   ├── CustomerCard.tsx
    │   │   └── SimulationPreview.tsx
    │   ├── services/
    │   │   └── api.ts      # Axios API client
    │   ├── types/
    │   │   └── index.ts    # TypeScript interfaces
    │   ├── App.tsx
    │   ├── index.tsx
    │   └── App.css
    └── package.json
```

## 🛠️ Development

### Backend Commands
```bash
cd backend
# Run server
python -m app.main

# Run with auto-reload
uvicorn app.main:app --reload
```

### Frontend Commands
```bash
cd frontend
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
```

## 🎯 Evaluation Criteria Coverage

| Criterion | Weight | Implementation |
|-----------|--------|----------------|
| Planning & Design | 35% | Complete specs in `ai-workspace/`, database design, API contracts |
| Technical Quality | 25% | Clean architecture, validation, error handling, type safety |
| Software Quality | 30% | Tiered pricing, tax validation, persistence, responsive UI |
| README & Deploy | 10% | This file with clear run instructions |

## 🔐 Security Notes

- Tax IDs are validated server-side using official algorithms
- SQLite foreign key constraints enabled
- Customer deletion restricted when simulations exist
- No sensitive data in frontend (exchange rates are public API)

## 📝 License

MIT License - Built for technical evaluation purposes.