
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

## 7. Pending Activities

The following activities remain pending:

- [ ] Complete the AI interaction documentation.
- [ ] Define the testing strategy.
- [ ] Review consistency across all planning documents.
- [ ] Implement the backend.
- [ ] Implement the frontend.
- [ ] Integrate the frontend and backend.
- [ ] Execute automated and manual tests.
- [ ] Complete the main README and deployment instructions.

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
