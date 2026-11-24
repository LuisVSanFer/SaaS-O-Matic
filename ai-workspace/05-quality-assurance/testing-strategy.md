
# Testing Strategy

## 1. Purpose

This document defines the testing strategy for SaaS-O-Matic.

The objective is to ensure that the application behaves according to its documented requirements and specifications.

Testing will be performed incrementally throughout development to identify defects early and maintain software quality.

The strategy covers backend functionality, business logic, database operations, API endpoints, frontend behavior, and application integration.

## 2. Testing Principles

The following principles will guide the testing process:

- **Early testing:** Tests should be implemented alongside application features rather than postponed until the end.
- **Specification-driven testing:** Expected behavior must be derived from the documented requirements and module specifications.
- **Isolation:** Business logic should be tested independently of external services and infrastructure whenever possible.
- **Repeatability:** Automated tests must produce consistent results.
- **Coverage of edge cases:** Boundary conditions and invalid inputs must be tested.
- **Regression prevention:** Previously implemented functionality must continue working after changes.

## 3. Testing Levels

The project will use the following testing levels:

### 3.1. Unit Testing

Unit tests verify individual functions and components in isolation.

They will primarily cover:

- Progressive pricing calculations.
- Tax calculations.
- Tax identification validation.
- Input validation.
- Data transformation and utility functions.

The main objective is to verify that individual pieces of business logic behave correctly.

### 3.2. Integration Testing

Integration tests verify that multiple components work correctly together.

They will cover:

- API endpoints interacting with the database.
- Customer creation and persistence.
- Simulation creation and persistence.
- Customer and simulation relationships.
- Currency exchange service integration, using mocked external responses where appropriate.

### 3.3. End-to-End Testing

End-to-end tests verify complete application workflows from the user's perspective.

Planned scenarios include:

- Creating a customer through the frontend.
- Searching for an existing customer.
- Opening customer details.
- Creating a simulation.
- Viewing the resulting price and tax.
- Reviewing the customer's simulation history.
- Displaying converted amounts in another currency.

## 4. Backend Testing Strategy

The backend will use Pytest as its primary testing framework.

### 4.1. Customer Module

Tests will verify:

- Successful customer creation.
- Missing required fields.
- Invalid email addresses.
- Invalid country codes.
- Unsupported subscription plans.
- Valid Spanish DNI/NIF identifiers.
- Valid Spanish CIF identifiers.
- Invalid tax identification numbers.
- Duplicate tax IDs within the same country.
- Customer search by company name.
- Customer search by tax ID.
- Retrieval of existing customers.
- Retrieval of non-existent customers.

### 4.2. Simulation Module

Tests will verify:

- Successful simulation creation.
- Simulation creation for non-existent customers.
- Negative active user counts.
- Negative storage values.
- Negative API call estimates.
- Non-integer active user counts.
- Correct persistence of simulation parameters.
- Correct persistence of calculated monetary values.
- Retrieval of simulations by ID.
- Retrieval of customer simulation history.
- Correct chronological ordering of simulation history.
- Preservation of historical simulation results.

### 4.3. Pricing Engine

The Pricing Engine will receive dedicated unit tests.

Expected results include:

| Active Users | Expected Base Price |
|---:|---:|
| 0 | €0 |
| 1 | €10 |
| 10 | €100 |
| 11 | €108 |
| 15 | €140 |
| 50 | €420 |
| 51 | €425 |
| 60 | €470 |
| 100 | €670 |

Additional tests will verify:

- Negative values are rejected.
- Non-integer values are rejected.
- Each pricing tier is applied progressively.
- Boundary conditions are handled correctly.
- Monetary calculations avoid binary floating-point arithmetic.

### 4.4. Tax Calculation

Tests will verify:

- Correct tax calculation for supported tax scenarios.
- Correct final price calculation.
- Consistent monetary rounding.
- Correct handling of zero-value simulations.
- Preservation of the applied tax rate in historical simulations.

Tax test cases must use explicitly defined tax scenarios rather than assuming that every customer in a country is subject to the same tax treatment.

## 5. Frontend Testing Strategy

Frontend testing will focus on component behavior and user interactions.

Planned tests include:

- Correct rendering of the dashboard.
- Customer search behavior.
- Customer creation form validation.
- Simulation form validation.
- Dynamic price updates when the number of users changes.
- Correct display of calculated amounts.
- Correct display of customer simulation history.
- Handling of backend errors.
- Handling of currency conversion failures.

The frontend testing tools will be selected during frontend implementation.

## 6. External Service Testing

The currency exchange API is an external dependency and must not make automated tests unreliable.

Tests will use mocked API responses to simulate:

- Successful exchange rate retrieval.
- Unsupported currencies.
- Invalid API responses.
- Network errors.
- External service unavailability.

The application must handle these situations gracefully without modifying stored simulation results or displaying misleading converted amounts.

## 7. Test Environment and Data

Automated tests must run independently of the development database.

The testing environment will use a separate temporary SQLite database.

Test data should be created specifically for each test or test group.

Tests must not depend on execution order or on records created manually during development.

External services should be mocked whenever possible to ensure repeatability.

## 8. Quality Assurance and Regression Testing

Before considering a feature complete:

1. Review the relevant specification.
2. Implement the feature.
3. Execute the corresponding automated tests.
4. Verify expected behavior manually when appropriate.
5. Fix identified defects.
6. Execute relevant regression tests.

A feature must not be considered complete solely because it works in a single manual execution.

## 9. Acceptance Criteria

The testing strategy will be considered successfully applied when:

- [ ] Core business logic has automated unit tests.
- [ ] Customer API endpoints have integration tests.
- [ ] Simulation API endpoints have integration tests.
- [ ] Pricing boundary conditions are covered.
- [ ] Tax calculations are tested against defined scenarios.
- [ ] Database persistence and relationships are verified.
- [ ] External API failures are tested.
- [ ] Frontend validation and interactions are tested.
- [ ] Main application workflows are verified end to end.
- [ ] Tests can be executed using documented instructions.
- [ ] Existing functionality is checked after relevant changes.

## 10. Continuous Quality Improvement

Testing will be an ongoing activity throughout development.

New tests should be added whenever new functionality is introduced or a defect is corrected.

The testing strategy may be updated as the application evolves and additional requirements or technical constraints are identified.
