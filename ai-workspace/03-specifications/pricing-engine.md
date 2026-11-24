
# Pricing Engine Specification

## 1. Overview

The Pricing Engine is responsible for calculating the base subscription price based on the number of active users.

It implements a progressive pricing model in which different prices apply to different user ranges.

The Pricing Engine must be independent of the API layer and database implementation to facilitate testing and future modifications.

## 2. Pricing Rules

The subscription price is calculated using the following progressive pricing tiers:

| User Range | Price per User |
|---|---:|
| 1–10 | €10 |
| 11–50 | €8 |
| More than 50 | €5 |

Each price applies exclusively to users within its corresponding range.

Users must not be charged at a single rate based on the total number of users.

## 3. Calculation Formula

Let `n` represent the number of active users.

The base subscription price is calculated as:

```text
Base Price(n) =
    10 × min(n, 10)
  +  8 × min(max(n - 10, 0), 40)
  +  5 × max(n - 50, 0)
```

The resulting amount is expressed in EUR.

### 3.1. Calculation Examples

**Example 1: 5 users**

```text
5 × €10 = €50
```

Base price: **€50**

**Example 2: 15 users**

```text
10 × €10 = €100
 5 ×  €8 =  €40
----------------
Total     = €140
```

Base price: **€140**

**Example 3: 60 users**

```text
10 × €10 = €100
40 ×  €8 = €320
10 ×  €5 =  €50
----------------
Total     = €470
```

Base price: **€470**

## 4. Input Validation

The Pricing Engine accepts the number of active users as its input.

The following rules apply:

- The number of users must be an integer.
- Negative values are not allowed.
- Zero users are allowed and produce a base price of €0.
- The Pricing Engine must reject invalid input rather than silently modifying it.

## 5. Monetary Precision

All financial calculations must use precise decimal arithmetic.

The implementation must not rely on binary floating-point arithmetic for monetary calculations.

The calculated base price will be converted to integer cents before persistence.

Since all current tier prices are whole euros, the resulting base price will always have two decimal places or fewer.

## 6. Expected Results

The following table defines the expected output for representative user counts:

| Active Users | Expected Base Price |
|---:|---:|
| 0 | €0 |
| 1 | €10 |
| 5 | €50 |
| 10 | €100 |
| 11 | €108 |
| 15 | €140 |
| 20 | €180 |
| 50 | €420 |
| 51 | €425 |
| 60 | €470 |
| 100 | €670 |

These values will be used as reference cases for automated tests.

## 7. Edge Cases

The implementation must correctly handle the following boundary conditions:

- **Zero users:** The resulting price must be €0.
- **First tier boundary:** 10 users must cost €100.
- **Second tier boundary:** 11 users must cost €108.
- **Second tier maximum:** 50 users must cost €420.
- **Third tier boundary:** 51 users must cost €425.
- **Large user counts:** The calculation must continue applying the third tier to every user above 50.

## 8. Business Rules

- **PRICE-BR-01:** The subscription price depends exclusively on the number of active users.
- **PRICE-BR-02:** Pricing tiers are progressive and cumulative.
- **PRICE-BR-03:** Each tier applies only to users within its corresponding range.
- **PRICE-BR-04:** Negative user counts are rejected.
- **PRICE-BR-05:** Zero users produce a base price of €0.
- **PRICE-BR-06:** All calculations use EUR as the base currency.
- **PRICE-BR-07:** Monetary calculations use precise decimal arithmetic.
- **PRICE-BR-08:** Storage and estimated API calls do not affect the current subscription price.

## 9. Acceptance Criteria

The Pricing Engine will be considered complete when:

- [ ] The calculation follows the progressive pricing model.
- [ ] Each pricing tier is applied correctly.
- [ ] Zero users produce a price of €0.
- [ ] Negative user counts are rejected.
- [ ] Non-integer user counts are rejected.
- [ ] All expected results match the reference table.
- [ ] Boundary conditions are covered by automated tests.
- [ ] Monetary calculations avoid binary floating-point arithmetic.
- [ ] The pricing logic can be tested independently of the API and database.
