# Browser Quick-Test Plan (Manual QA)

**Target URL:** http://192.168.1.73:3000 (or http://localhost:3000 local)

---

## 🧪 Test Suite: Customer Management

### TC-01: Create Customer - Valid Spanish DNI
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click "Nuevo Cliente" | Modal opens |
| 2 | Fill: Empresa="Test DNI", NIF="52892374X", Email="dni@test.com", País="ES", Plan="Basic" | Form accepts input |
| 3 | Click "Crear" | Toast success, customer appears in list |
| 4 | Verify tax_id shows "52892374X" | ✅ |

### TC-02: Create Customer - Valid Spanish NIE (Y/Z prefix)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click "Nuevo Cliente" | Modal opens |
| 2 | Fill: Empresa="Test NIE Y", NIF="Y8765432P", Email="niey@test.com", País="ES" | Form accepts |
| 3 | Click "Crear" | ✅ Success |
| 4 | Repeat with Z9999999H | ✅ Success |

### TC-03: Create Customer - Valid Spanish CIF
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click "Nuevo Cliente" | Modal opens |
| 2 | Fill: Empresa="Test CIF", NIF="B87654323", Email="cif@test.com", País="ES", Plan="Professional" | Form accepts |
| 3 | Click "Crear" | ✅ Success |
| 4 | Test letter control: P1111111I | ✅ Success |

### TC-04: Create Customer - Invalid Spanish Tax ID (Rejected)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click "Nuevo Cliente" | Modal opens |
| 2 | Fill: Empresa="Bad Tax", NIF="12345678A", País="ES" | Form accepts |
| 3 | Click "Crear" | ❌ Toast error: "Error al crear cliente: NIF/CIF inválido. Verifique el formato." |
| 4 | Customer NOT created | ✅ |

### TC-05: Create Customer - Non-Spain (No Spanish Validation)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click "Nuevo Cliente" | Modal opens |
| 2 | Fill: Empresa="German Corp", NIF="INVALID123", Email="de@test.com", País="DE" | Form accepts |
| 3 | Click "Crear" | ✅ Success (no Spanish tax validation) |
| 4 | Verify tax_id stored as "INVALID123" | ✅ |

### TC-06: Duplicate Tax ID Same Country (Rejected)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Create customer with B87654323, ES | ✅ Success |
| 2 | Create another with same tax_id, ES | ❌ Toast error: "Error al crear cliente: Ya existe un cliente con este NIF/CIF en el mismo país." |

### TC-07: Same Tax ID Different Country (Allowed)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Create customer with B87654323, ES | ✅ Success |
| 2 | Create another with B87654323, DE | ✅ Success |

---

## 🧪 Test Suite: Simulation Preview (Live Calculator)

### TC-08: Preview Updates on Slider Change
| Step | Action | Expected |
|------|--------|----------|
| 1 | Select a customer from list | Customer card shows |
| 2 | Move "Usuarios activos" slider | Preview updates instantly (no save) |
| 3 | Verify base price changes at tiers: 10→11 users (€100→€108), 50→51 (€420→€425) | ✅ |

### TC-09: Preview Updates on Numeric Input Change
| Step | Action | Expected |
|------|--------|----------|
| 1 | Type directly in "Usuarios activos" number input | Preview updates on blur/enter |
| 2 | Verify slider position matches input | ✅ Synced |

### TC-10: Currency Selector Changes Display Only
| Step | Action | Expected |
|------|--------|----------|
| 1 | Select customer, open preview | Shows EUR |
| 2 | Change currency to USD | Amounts convert, badge shows "USD (rate: X.XX)" |
| 3 | Change to GBP | Converts again |
| 4 | Switch back to EUR | Shows original EUR amounts, rate 1.0 |

### TC-11: Storage & API Calls Editable
| Step | Action | Expected |
|------|--------|----------|
| 1 | In preview, change "Almacenamiento (GB)" slider/input | Value updates |
| 2 | Change "Llamadas API estimadas" slider/input | Value updates |
| 3 | Verify these don't affect base price (informational only) | ✅ |

### TC-12: Preview ≠ Persisted (No DB Write)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Adjust sliders in preview | Preview changes |
| 2 | Refresh page / navigate away | No simulation created in history |
| 3 | Click "Guardar simulación" | NOW appears in history |

---

## 🧪 Test Suite: Simulation History

### TC-13: Save Simulation Persists Calculated Values
| Step | Action | Expected |
|------|--------|----------|
| 1 | Set: 15 users, 100 GB, 50000 API calls | Preview shows calculated totals |
| 2 | Click "Guardar simulación" | Toast success, entry appears in history |
| 3 | Verify history shows: base=14000¢, tax=2940¢, total=16940¢ (21% ES) | ✅ |

### TC-14: Multiple Simulations Independent
| Step | Action | Expected |
|------|--------|----------|
| 1 | Save sim A: 10 users | History shows 12100¢ total |
| 2 | Save sim B: 20 users | History shows 21780¢ total |
| 3 | Verify both preserved with their own values | ✅ |

### TC-15: Simulation Displayed in Currently Selected Currency
| Step | Action | Expected |
|------|--------|----------|
| 1 | Preview in USD, save | Simulation stored in EUR cents (backend) |
| 2 | Later view with USD selected | Amounts shown converted to USD with current rate |
| 3 | Switch to EUR | Amounts shown in original EUR cents (no conversion) |

---

## 🧪 Test Suite: Delete Confirmations

### TC-16: Delete Simulation Asks Confirmation
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click 🗑️ on a simulation row | Browser confirm dialog: "¿Eliminar esta simulación?" |
| 2 | Click "Cancelar" | Simulation remains |
| 3 | Click 🗑️ again, click "Aceptar" | Simulation removed, toast success |

### TC-17: Delete Customer Asks Confirmation
| Step | Action | Expected |
|------|--------|----------|
| 1 | Click 🗑️ on customer card | Browser confirm: "¿Eliminar cliente y TODAS sus simulaciones?" |
| 2 | Click "Cancelar" | Customer remains |
| 3 | Click 🗑️ again, click "Aceptar" | Customer + all simulations removed |

### TC-18: Delete Customer Cascades Simulations
| Step | Action | Expected |
|------|--------|----------|
| 1 | Create customer with 3 simulations | All visible |
| 2 | Delete customer (confirm) | Customer gone, simulations gone |

---

## 🧪 Test Suite: Search & Filter

### TC-19: Search by Company Name
| Step | Action | Expected |
|------|--------|----------|
| 1 | Type in search box "Test" | List filters to matching names |
| 2 | Clear search | All customers shown |

### TC-20: Search by Tax ID
| Step | Action | Expected |
|------|--------|----------|
| 1 | Type "B87654323" | Shows that customer |

### TC-21: Search by Company Name or Tax ID (Email not searchable)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Type "@test.com" | No results (search limited to company name and tax ID) |
| 2 | Type "B87654323" or "Test" | Shows matching customers |

---

## 🧪 Test Suite: Responsive / Edge Cases

### TC-22: Mobile View (Resize Browser)
| Step | Action | Expected |
|------|--------|----------|
| 1 | Resize to < 640px width | Layout stacks, cards full width |
| 2 | Test all interactions on mobile | Touch-friendly |

### TC-23: Empty States
| Step | Action | Expected |
|------|--------|----------|
| 1 | Fresh DB (or delete all) | "No hay clientes. Crea uno nuevo." |
| 2 | Customer with no simulations | "Sin simulaciones guardadas" |

### TC-24: Network Error Handling
| Step | Action | Expected |
|------|--------|----------|
| 1 | Stop backend server | Frontend shows toast errors on actions |
| 2 | Restart backend | Actions work again |

### TC-25: Large Numbers
| Step | Action | Expected |
|------|--------|----------|
| 1 | Set users=1000 in preview | Calculates correctly (517000¢ base) |
| 2 | Set storage=10000 GB | Accepts large values |

---

## ✅ Quick Smoke Test (2 min)

Run these 5 tests before any deploy:

1. **Create** → Spanish customer with valid CIF (B87654323)
2. **Preview** → Move sliders, verify tier jumps at 10/11 and 50/51 users
3. **Currency** → Switch EUR→USD→EUR, verify conversion
4. **Save** → Click "Guardar simulación", verify history entry
5. **Delete** → Delete simulation (confirm), delete customer (confirm)

---

## 🐛 Known Issues to Verify Fixed

| Issue | Test | Status |
|-------|------|--------|
| CIF validation rejected valid B87654321 | TC-03 | ✅ Fixed (use B87654323) |
| NIE Y/Z prefixes rejected | TC-02 | ✅ Fixed (use Y8765432P, Z9999999H) |
| Slider/input out of sync | TC-09 | ✅ Controlled components |
| No delete confirmation | TC-16, TC-17 | ✅ window.confirm added |
| Currency hardcoded EUR | TC-10 | ✅ Dynamic conversion |
| Preview persisted to DB | TC-12 | ✅ Preview endpoint separate |

---

## 📝 Test Data Reference

### Valid Spanish Tax IDs for Testing
| Type | Value | Notes |
|------|-------|-------|
| DNI | 52892374X | Control X |
| DNI | 12345678Z | Control Z |
| NIE (X) | X1234567L | Control L |
| NIE (Y) | Y8765432P | Control P |
| NIE (Z) | Z9999999H | Control H |
| CIF | B87654323 | Control 3 |
| CIF | A12345674 | Control 4 |
| CIF | G55555551 | Control 1 |
| CIF | Q12345674 | Control 4 |
| CIF (letter) | P1111111I | Control I=1 |

### Tier Boundaries (users → base €)
| Users | Base (¢) | Base (€) |
|-------|----------|----------|
| 10 | 10000 | 100.00 |
| 11 | 10800 | 108.00 |
| 50 | 42000 | 420.00 |
| 51 | 42500 | 425.00 |
| 100 | 67000 | 670.00 |