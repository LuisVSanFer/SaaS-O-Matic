## 1. Functional Requirements

El sistema debe cumplir los siguientes requisitos funcionales para garantizar la correcta gestión de clientes corporativos y la simulación de costes de consumo.

| ID | Requisito funcional | Prioridad |
|:---:|---|:---:|
| **RF-01** | Registrar clientes corporativos. | 🔴 Alta |
| **RF-02** | Validar identificadores fiscales según el país. | 🔴 Alta |
| **RF-03** | Buscar clientes por empresa o identificador fiscal. | 🔴 Alta |
| **RF-04** | Consultar los datos de un cliente. | 🔴 Alta |
| **RF-05** | Registrar simulaciones de consumo. | 🔴 Alta |
| **RF-06** | Calcular el coste mediante tarifas acumulativas por tramos. | 🔴 Alta |
| **RF-07** | Aplicar impuestos según el país del cliente. | 🔴 Alta |
| **RF-08** | Consultar el historial de simulaciones. | 🔴 Alta |
| **RF-09** | Convertir los importes a diferentes divisas. | 🔴 Alta |
| **RF-10** | Ajustar dinámicamente los parámetros de consumo. | 🔴 Alta |

### Resumen
- **Total de requisitos:** 10
- **Prioridad alta:** 10

---

## 2. Non-Functional Requirements

Los siguientes requisitos definen las características técnicas, de calidad y funcionamiento que debe cumplir el sistema.

| ID | Requisito no funcional |
|:---:|---|
| **RNF-01** | El código debe estar organizado modularmente. |
| **RNF-02** | La API debe validar los datos recibidos. |
| **RNF-03** | Los errores deben comunicarse claramente al usuario. |
| **RNF-04** | La interfaz debe ser responsive. |
| **RNF-05** | Los datos deben persistir en SQLite. |
| **RNF-06** | Las operaciones con la base de datos deben mantener la integridad de los datos. |
| **RNF-07** | Las credenciales y configuraciones sensibles no deben exponerse en el repositorio. |
| **RNF-08** | El sistema debe contemplar errores de comunicación con servicios externos. |
| **RNF-09** | El proyecto debe poder ejecutarse localmente siguiendo las instrucciones del README. |
| **RNF-10** | La lógica de negocio debe poder probarse independientemente de la interfaz. |

---

## 3. Open Questions and Ambiguities

Durante el análisis de requisitos se han identificado varias cuestiones que necesitan aclaración antes de definir completamente la lógica de negocio y la implementación del sistema.

### 3.1. Impuestos

¿Qué tipo de IVA se debe aplicar en cada país?

- ¿Se utilizarán tipos impositivos fijos definidos en el sistema?
- ¿Se consultará una fuente externa para obtener los tipos actualizados?

### 3.2. Planes

El registro de clientes solicita la selección de un plan, pero no se especifican los planes disponibles ni sus condiciones.

- ¿Qué planes estarán disponibles?
- ¿Cómo afecta cada plan al precio final?
- ¿Existen límites de consumo asociados a cada plan?

### 3.3. Almacenamiento y llamadas API

Los parámetros de almacenamiento y número de llamadas API se solicitan durante la simulación, pero no se especifica cómo afectan al cálculo de la factura.

- ¿Se aplicarán tarifas específicas por almacenamiento?
- ¿Existirá un coste por cada llamada API?
- ¿Se incluirán estos conceptos en el cálculo por tramos?

### 3.4. Divisas

No se especifica cómo deben gestionarse las conversiones monetarias.

- ¿La conversión se realizará únicamente para mostrar los importes en diferentes divisas?
- ¿También se almacenarán los importes convertidos?
- ¿Qué fuente se utilizará para obtener los tipos de cambio?

### 3.5. Identificadores fiscales

España requiere una validación estricta de los identificadores fiscales, pero no se especifican los tipos de documentos extranjeros que deben admitirse.

- ¿Qué identificadores fiscales internacionales estarán soportados?
- ¿Se validará cada identificador mediante reglas específicas según el país?

### 3.6. Usuarios activos

No se especifican las restricciones del parámetro de usuarios activos durante las simulaciones.

- ¿Se permiten valores decimales?
- ¿Cuál es el número máximo de usuarios activos?
- ¿Debe existir un valor mínimo?

### 3.7. Impuestos internacionales

No se especifica cómo deben tratarse las operaciones B2B internacionales.

- ¿Cómo se gestionarán las operaciones intracomunitarias?
- ¿Se contemplarán las exenciones fiscales?
- ¿Cómo se aplicará la inversión del sujeto pasivo (*Reverse Charge*)?

---

**Nota:** Las cuestiones anteriores quedan pendientes de definición y deberán resolverse antes de establecer definitivamente las reglas de negocio correspondientes.


## 4. Business Rules

### BR-01: Customer Registration and Validation

- Every customer must have a unique identifier.
- Company name, tax identifier, contact email, country and selected plan are mandatory.
- Tax identifiers must be validated according to the selected country.
- For Spain, DNI, NIF and CIF identifiers must pass the corresponding official control algorithms.
- Duplicate tax identifiers within the same country are not allowed.
- Tax identifiers should be normalized before validation and storage (e.g., removing unnecessary spaces and hyphens).

### BR-02: Tiered Pricing Calculation

The monthly subscription cost must be calculated using an accumulative tiered pricing model.

| Tier | Number of Users | Price per User |
|---|---:|---:|
| Tier 1 | 1–10 | €10 |
| Tier 2 | 11–50 | €8 |
| Tier 3 | More than 50 | €5 |

The pricing calculation follows these rules:

- The first 10 users are charged €10 each.
- Users from 11 to 50 are charged €8 each.
- Users above 50 are charged €5 each.
- Each tier is calculated independently and accumulated to obtain the base monthly cost.
- Zero users result in a base cost of €0.
- Negative user quantities are not allowed.

**Expected calculation examples:**

| Active Users | Base Monthly Cost |
|---:|---:|
| 0 | €0 |
| 1 | €10 |
| 10 | €100 |
| 11 | €108 |
| 15 | €140 |
| 50 | €420 |
| 51 | €425 |
| 100 | €670 |

### BR-03: Tax Calculation

- Taxes must be calculated on top of the base monthly subscription cost.
- The applicable tax rate depends on the customer's country and the business tax rules defined for the system.
- The final monthly amount is the sum of the base cost and the applicable tax.
- Monetary calculations must use decimal arithmetic to avoid floating-point precision errors.
- Tax amounts must follow a consistent rounding policy.

### BR-04: Simulation Management

- Every simulation must belong to an existing customer.
- Each simulation must record:
  - Number of active users.
  - Contracted storage capacity.
  - Estimated API calls.
- The backend must calculate the monthly subscription cost.
- Simulation results must be persisted in the database.
- Historical simulations must preserve the original calculation results, even if pricing or tax rules change in the future.

### BR-05: Currency Conversion

- EUR is the system's base currency.
- All subscription costs must initially be calculated and stored in EUR.
- Currency conversion is exclusively intended for displaying monetary values in the selected currency.
- Exchange rates must be retrieved from an external public API.
- If the external API is unavailable, the application must communicate the issue and avoid displaying misleading converted amounts.
- Currency conversion must not modify the original amounts stored in the database.

## 5. Business Decisions

### BD-001: Storage and API Usage Pricing

**Decision:** Storage consumption and estimated API calls will be recorded in each simulation but will not contribute to the monthly subscription cost.

**Context:** The project requirements request these parameters as simulation inputs but do not specify any associated pricing rules.

**Alternatives considered:**
- Option A: Record these parameters without charging for them.
- Option B: Introduce additional pricing rules for storage and API calls.

**Rationale:** Option A was selected to avoid introducing unsupported business rules or inventing pricing information not provided by the company.

**Consequences:**
- Both parameters will be persisted in the database.
- Both parameters will be displayed in the simulation history.
- Neither parameter will affect the calculated monthly cost.
- Future pricing extensions can incorporate these parameters without redesigning the entire system.
