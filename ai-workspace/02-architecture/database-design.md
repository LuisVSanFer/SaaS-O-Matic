
# Database Design

## 1. Overview

SaaS-O-Matic will use SQLite as its relational database.

The database will store customer information and subscription simulations. The design aims to maintain data integrity, avoid unnecessary duplication, and preserve historical simulation results.

## 2. Database Entities

The initial database will contain two main entities:

- **Customer:** Stores the information of each corporate customer.
- **Simulation:** Stores the consumption parameters and calculated pricing results for each simulation.

## 3. Entity Relationship

A customer can have multiple simulations, while each simulation belongs to exactly one customer.

```text
CUSTOMER (1) ───────── (N) SIMULATION
```

## 4. Table Definitions

### 4.1. Customer

Stores the information required to identify and manage corporate customers.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | Primary Key | Unique customer identifier |
| company_name | TEXT | NOT NULL | Company name |
| tax_id | TEXT | NOT NULL | Tax identification number |
| email | TEXT | NOT NULL | Contact email |
| country | TEXT | NOT NULL | Customer's country (ISO 3166-1 alpha-2) |
| plan | TEXT | NOT NULL | Selected subscription plan |
| created_at | DATETIME | NOT NULL | Record creation timestamp |

**Constraints and rules:**
- `id` is an auto-generated primary key.
- The combination of `country` and `tax_id` must be unique.
- Tax identification numbers must be validated before insertion.
- The `country` field will use ISO 3166-1 alpha-2 country codes (e.g. `ES`, `FR`, `DE`).

### 4.2. Simulation

Stores the consumption parameters and calculated pricing results associated with a customer.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | Primary Key | Unique simulation identifier |
| customer_id | INTEGER | Foreign Key, NOT NULL | Associated customer |
| active_users | INTEGER | NOT NULL | Number of active users |
| storage_gb | REAL | NOT NULL | Contracted storage in GB |
| estimated_api_calls | INTEGER | NOT NULL | Estimated API calls |
| base_amount_cents | INTEGER | NOT NULL | Base price in EUR cents |
| tax_rate | REAL | NOT NULL | Applied tax rate |
| tax_amount_cents | INTEGER | NOT NULL | Tax amount in EUR cents |
| total_amount_cents | INTEGER | NOT NULL | Final amount in EUR cents |
| created_at | DATETIME | NOT NULL | Simulation creation timestamp |

**Constraints and rules:**
- `customer_id` references `Customer.id`.
- A simulation cannot exist without an associated customer.
- Consumption values cannot be negative.
- `active_users` must be an integer.
- Monetary amounts are stored as integer cents to avoid floating-point precision issues.
- Prices are calculated and stored in EUR.
- Tax information and calculated amounts are stored as a snapshot, preserving historical results even if pricing or tax rules change.
- Storage and API calls are recorded but do not contribute to the current pricing calculation.

## 5. Relationships and Referential Integrity

- Each customer can have zero or more simulations.
- Each simulation belongs to exactly one customer.
- Foreign key constraints must be enabled in SQLite.
- Deleting a customer with existing simulations should be restricted to preserve historical records.

## 6. Data Integrity Considerations

- Customer tax IDs must be validated before being stored.
- Duplicate tax IDs within the same country are not allowed.
- Required fields must not accept NULL values.
- Numeric consumption values must be validated before insertion.
- Monetary calculations must use precise decimal arithmetic in the application layer.
- Monetary results are persisted as integer cents.

## 7. Design Decisions

### DB-001: Store storage and API call estimates

Storage and estimated API calls will be stored in each simulation and displayed in the simulation history. They will not contribute to the subscription price because the challenge does not define pricing rules for these parameters.

### DB-002: Store monetary values in cents

All monetary amounts will be stored as integer cents (EUR) to avoid floating-point precision errors.

### DB-003: Preserve simulation history

Simulation results will be stored as historical snapshots. Changes to customer information, pricing rules, or tax rates must not modify previously stored simulation results.

### DB-004: Restrict customer deletion

Customers with existing simulations cannot be deleted. This prevents accidental loss of historical business records.
