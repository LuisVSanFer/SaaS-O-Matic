
# System Architecture

## 1. Overview

SaaS-O-Matic follows a client-server architecture composed of a frontend application, a backend REST API, a relational database, and an external currency exchange rate service.

The system is designed with a clear separation of responsibilities to improve maintainability, testability, and scalability.

### Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Frontend | React + TypeScript + Vite | User interface and client-side interactions |
| Backend | Python + FastAPI | REST API, business logic and data validation |
| Database | SQLite | Persistent data storage |
| ORM | SQLAlchemy | Database access and object-relational mapping |
| Data validation | Pydantic | API request and response validation |
| External API | Exchange Rate API | Currency exchange rates |
| Testing | Pytest | Backend automated testing |
| Version control | Git + GitHub | Source code management |

## 2. High-Level Architecture

The application follows a layered client-server architecture.

```text
+----------------------------------+
|            FRONTEND              |
|                                  |
|       React + TypeScript         |
|                                  |
|  - Dashboard                     |
|  - Customer management           |
|  - Simulation forms              |
|  - Pricing visualization         |
|  - Currency conversion           |
+----------------+-----------------+
                 |
                 | HTTP / JSON
                 | REST API
                 v
+----------------------------------+
|             BACKEND              |
|                                  |
|             FastAPI              |
|                                  |
|  - API endpoints                 |
|  - Request validation            |
|  - Business logic                |
|  - Pricing engine                |
|  - Tax calculation               |
|  - Currency conversion service   |
|  - Data persistence              |
+-----------+----------------------+
            |
            | SQLAlchemy
            v
+----------------------------------+
|            DATABASE              |
|                                  |
|              SQLite              |
|                                  |
|  - Customers                     |
|  - Simulations                   |
+----------------------------------+

            |
            | HTTPS / JSON
            v
+----------------------------------+
|        EXTERNAL SERVICE          |
|                                  |
|        Exchange Rate API         |
|                                  |
|  - Currency exchange rates       |
+----------------------------------+
```

## 3. Component Responsibilities

### 3.1. Frontend

The frontend is responsible for presenting information and allowing sales representatives to interact with the application.

Its main responsibilities are:

- Displaying the customer dashboard.
- Searching and viewing customer information.
- Displaying customer simulation history.
- Providing forms to create customers and simulations.
- Updating pricing information dynamically when simulation parameters change.
- Displaying calculated prices, taxes, and totals.
- Converting EUR amounts into supported currencies for visualization.

The frontend communicates with the backend exclusively through the REST API.

### 3.2. Backend

The backend exposes the application's functionality through a REST API implemented with FastAPI.

It is responsible for:

- Receiving and validating API requests.
- Managing customer creation and retrieval.
- Validating tax identification numbers according to the customer's country.
- Creating and retrieving simulations.
- Calculating subscription prices using the defined progressive pricing rules.
- Applying the appropriate tax rules.
- Managing currency conversion requests.
- Persisting and retrieving application data.

The backend is the source of truth for business rules and financial calculations. The frontend may perform preliminary calculations for immediate feedback, but the backend must validate and recalculate all final results.

### 3.3. Database

SQLite is used as the application's relational database.

SQLAlchemy provides the abstraction layer between the backend and the database.

The database stores:

- Customer information.
- Simulation parameters.
- Calculated simulation results.

Historical simulation results are preserved independently of future changes to pricing or tax rules.

### 3.4. External Currency Exchange Service

The application uses an external exchange rate API to retrieve currency conversion rates.

The service will:

- Retrieve exchange rates using EUR as the base currency.
- Support at least EUR, USD, and GBP.
- Allow the frontend to display converted amounts.
- Handle external API failures without affecting stored simulation data.

Currency conversion is intended for display purposes. Original prices and persisted financial calculations remain in EUR.

## 4. Backend Internal Structure

The backend will follow a modular structure based on separation of concerns.

The main logical modules are:

| Module | Responsibility |
|---|---|
| API / Routers | Define HTTP endpoints and handle requests |
| Schemas | Validate incoming data and structure API responses |
| Models | Define database entities using SQLAlchemy |
| Services | Implement business logic and external integrations |
| Repositories / Data Access | Handle database queries and persistence |
| Core | Application configuration and shared infrastructure |

The pricing engine and tax calculation logic will be implemented as dedicated services to facilitate independent testing.

## 5. Data Flow

### 5.1. Customer Creation

1. The frontend sends customer information to the backend.
2. FastAPI validates the request structure using Pydantic.
3. The backend validates the customer's tax identification number.
4. The backend checks for duplicate tax IDs.
5. SQLAlchemy persists the customer in SQLite.
6. The backend returns the created customer information.

### 5.2. Simulation Creation

1. The frontend sends the customer ID and consumption parameters.
2. The backend validates the request.
3. The backend verifies that the customer exists.
4. The pricing engine calculates the base subscription price.
5. The tax service calculates the applicable tax.
6. The simulation results and input parameters are persisted in SQLite.
7. The backend returns the complete simulation result.

### 5.3. Currency Conversion

1. The frontend requests a currency conversion.
2. The backend retrieves the required exchange rate from the external API.
3. The backend converts the original EUR amount.
4. The converted amount is returned to the frontend.
5. The frontend displays the converted value without modifying the original simulation.

## 6. Architectural Principles

The following principles guide the implementation:

- **Separation of concerns:** Each component has a clearly defined responsibility.
- **Single source of truth:** Business rules and final financial calculations are enforced by the backend.
- **Modularity:** Business logic is separated into independent services.
- **Testability:** Core business logic can be tested independently of the API and database.
- **Data integrity:** Database constraints and backend validation protect stored information.
- **External service resilience:** Failures in the currency exchange API must not compromise existing customer or simulation data.
- **Historical consistency:** Previously saved simulations must retain their original calculated values.

## 7. Deployment Strategy

The initial version will be designed to run locally for development and evaluation.

The frontend and backend will run as separate applications:

- Frontend: Vite development server.
- Backend: FastAPI application served by Uvicorn.
- Database: Local SQLite database file.

The frontend will communicate with the backend through HTTP requests.

Deployment instructions and configuration details will be documented in the main project README.

## 8. Architecture Decisions

### AD-001: Separate frontend and backend

The frontend and backend will be developed as independent applications communicating through a REST API. This separation allows each component to evolve independently.

### AD-002: Backend as the source of truth

All final pricing and tax calculations will be performed and validated by the backend. Frontend calculations are only intended to provide immediate visual feedback.

### AD-003: EUR as the base currency

All financial calculations and persisted monetary amounts will use EUR. Currency conversion will only affect displayed values.

### AD-004: Modular backend structure

The backend will be divided into modules with specific responsibilities to facilitate maintenance and automated testing.

### AD-005: External API isolation

Currency exchange rate retrieval will be encapsulated in a dedicated service, preventing external API dependencies from spreading throughout the application.
