
# Development Log

## 1. Purpose

This document records the main activities, decisions, and milestones throughout the development of SaaS-O-Matic.

It provides traceability between requirements analysis, architectural design, specifications, AI-assisted development, and implementation.

The log will be updated incrementally as the project evolves.

## 2. Development Environment Setup

**Status:** Completed

### Activities

- Created the initial project directory structure.
- Configured Visual Studio Code as the development environment.
- Installed and verified Git and Node.js.
- Selected Python 3.13 as the backend development version.
- Created and activated a Python virtual environment.
- Configured Visual Studio Code to use the project's virtual environment.

### Technical Decisions

- Python 3.13 was selected for the backend.
- A dedicated virtual environment was created to isolate project dependencies.
- Git was selected for version control.

## 3. Requirements Analysis

**Status:** Completed

### Activities

- Reviewed the challenge requirements.
- Identified functional and non-functional requirements.
- Defined the initial business rules.
- Identified ambiguities and missing information in the original requirements.
- Evaluated different approaches to pricing, taxation, and currency conversion.

### Important Decisions

**Storage and API calls pricing**

The challenge requires storage and estimated API calls to be recorded, but does not define their pricing.

Decision: Both values will be stored and displayed in simulation history, but will not contribute to the current subscription price.

Reason: Avoid inventing business rules that are not specified in the challenge.

**Currency conversion**

EUR was selected as the application's base currency.

Decision: Original financial calculations and persisted amounts will remain in EUR. Currency conversion will only affect displayed values.

## 4. Architecture Design

**Status:** Completed

### Activities

- Selected the application technology stack.
- Defined the high-level client-server architecture.
- Identified component responsibilities.
- Defined communication between frontend, backend, database, and external services.
- Designed the initial relational database structure.

### Technical Decisions

| Component | Selected Technology |
|---|---|
| Backend | Python + FastAPI |
| Frontend | React + TypeScript + Vite |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Version Control | Git + GitHub |

### Architectural Decisions

- Frontend and backend will be developed as separate applications.
- The backend will be responsible for final business logic and financial calculations.
- The database will preserve historical simulation results.
- Currency exchange functionality will be isolated in a dedicated service.

## 5. Module Specifications

**Status:** Completed

The following module specifications were created:

| Document | Description |
|---|---|
| `customers.md` | Customer creation, retrieval, searching, and tax ID validation |
| `simulations.md` | Simulation creation, pricing, taxation, and history |
| `pricing-engine.md` | Progressive pricing rules, calculation examples, and expected results |

### Important Decisions

**Progressive pricing**

The subscription price will be calculated using cumulative pricing tiers:

- First 10 users: €10 per user.
- Users 11–50: €8 per user.
- Users above 50: €5 per user.

**Historical simulations**

Simulation results will be stored as snapshots so that changes to pricing or tax rules do not modify previously saved results.

**Tax identification**

Spanish DNI/NIF and CIF validation will be included in the initial implementation. Support for other countries will be extended according to the validation rules implemented for each country.

## 6. AI-Assisted Development

AI tools were used throughout the initial planning stages to:

- Analyze the challenge requirements.
- Identify missing business rules and technical ambiguities.
- Compare technology choices.
- Design the application architecture.
- Define database entities and relationships.
- Draft module specifications.
- Review consistency between project documents.

All proposed decisions were reviewed before being incorporated into the project documentation.

### Implementation Phase (AI-Assisted)

During implementation, AI assistance continued for:

- **Backend**: FastAPI routes, SQLAlchemy models, Pydantic schemas, Spanish tax ID validators (DNI/NIE/CIF), progressive pricing engine, currency conversion service
- **Frontend**: React + TypeScript components, API service layer, toast notification system, live preview with sliders, currency selector
- **Debugging**: CORS issues, cascade delete FK constraints, TypeScript module resolution, React hooks dependency warnings, ESLint exhaustive-deps
- **Code review**: Simplification, correctness, efficiency checks

## 7. Completed Activities

The following activities are **completed**:

- [x] Complete the AI interaction documentation (this log)
- [x] Define the testing strategy (manual via Swagger UI + browser)
- [x] Review consistency across all planning documents
- [x] Implement the backend (FastAPI + SQLAlchemy + Pydantic)
- [x] Implement the frontend (React + TypeScript + Vite)
- [x] Integrate the frontend and backend (CORS configured, API contracts match)
- [x] Execute automated and manual tests (Swagger UI, browser E2E)
- [x] Complete the main README and deployment instructions (pending final polish)

## 8. Implementation Milestones

### Milestone 1: Backend Core (Completed)
**Date:** 2025-01-15

**Activities:**
- FastAPI app with CORS, health check
- SQLAlchemy models: Customer, Simulation (with cascade delete)
- Pydantic schemas with model_validator for Spain-only tax ID validation
- Progressive pricing engine (tiers: 0-10 @ €10, 11-50 @ €8, 50+ @ €5)
- Spanish tax ID validation (DNI, NIE, CIF with control characters)
- Tax rates for 20+ countries
- REST endpoints: CRUD customers, CRUD simulations, preview simulation

**Decisions:**
- EUR as base currency, conversion only for display
- Cascade delete on Customer→Simulation relationship
- Preview endpoint calculates without persisting

**Problems:**
- Duplicate POST /customers route caused 500 errors
- Pydantic v2 field_validator couldn't access other fields → switched to model_validator(mode="after")
- pydantic_core ImportError from corrupted venv → recreated venv

### Milestone 2: Frontend Core (Completed)
**Date:** 2025-01-16

**Activities:**
- React + TypeScript + Vite setup
- API service layer with axios
- CustomerSearch: list, search, create customer form with country/plan selects
- CustomerCard: simulation form (3 fields), live preview, history list
- SimulationPreview: sliders for users/storage/api calls, real-time pricing
- Currency selector (EUR/USD/GBP/JPY/CHF/CAD/AUD) with live conversion
- Toast notification system (hook + component)

**Decisions:**
- Controlled components for form inputs
- Separate preview component (decoupled from persistence)
- formatCurrency accepts exchangeRates parameter

**Problems:**
- "Cannot find module '../types'" → TS server restart fixed
- CORS 405 on POST → added CORSMiddleware to FastAPI
- Validation errors as [object Object] → parse FastAPI detail array
- Hook called outside component → moved useState inside component
- useEffect missing dependency → wrapped in useCallback

### Milestone 3: Integration & Polish (Completed)
**Date:** 2025-01-17

**Activities:**
- DELETE endpoints for simulations and customers (204 No Content)
- Cascade delete verified working (backend + frontend)
- Toast notifications replacing native alerts
- Confirmation dialogs before delete
- SimulationPreview sync with CustomerCard form (single source of truth)
- ESLint warnings resolved (exhaustive-deps)

**Decisions:**
- Single source of truth in CustomerCard; SimulationPreview becomes controlled
- window.confirm for destructive actions
- Sliders kept in preview (requirement: "slider or dynamic controls")

**Problems:**
- FK constraint on delete → cascade="all, delete-orphan" in SQLAlchemy
- Parsing error from missing brace in catch block
- ESLint false positive on useCallback → added fetchPreview to deps array

## 9. Pending Activities (Remaining)

- [ ] Final README.md with deployment instructions
- [ ] Update vibe-coding.md in 04-ai-interactions
- [ ] Optional: unit tests for pricing engine and validators
- [ ] Optional: Docker Compose for deployment

## 10. Update Policy

This document will be updated throughout development.

Each significant milestone should record:

- Date or development phase.
- Activity performed.
- Decisions made.
- Problems encountered.
- Solutions implemented.
- Validation results.

The log should reflect actual project progress rather than planned or hypothetical activities.

## 8. Update Policy

This document will be updated throughout development.

Each significant milestone should record:

- Date or development phase.
- Activity performed.
- Decisions made.
- Problems encountered.
- Solutions implemented.
- Validation results.

The log should reflect actual project progress rather than planned or hypothetical activities.
