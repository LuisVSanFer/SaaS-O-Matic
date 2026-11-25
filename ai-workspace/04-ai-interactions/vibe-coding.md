# Vibe Coding Log — SaaS-O-Matic

## What is "Vibe Coding" Here

This document captures the *actual* development experience — not the idealized version. It records how AI assistance was used in practice, what worked, what didn't, and the real decisions made under uncertainty.

---

## Phase 1: Project Setup & Requirements (Days 1-2)

### Approach
- Started with a vague challenge description
- Used AI to extract requirements, identify gaps, propose architecture
- **Key insight**: The challenge didn't specify storage/API call pricing → decided to store but not price them

### AI Role
- Requirements engineering assistant
- Architecture proposer (FastAPI + React + SQLite)
- Technology comparison

### Human Decisions
- Python 3.13, virtual env, Git from day 1
- Separate frontend/backend folders
- EUR as base currency (conversion only for display)

### Friction Points
- "Should I use venv or not?" — basic env questions that AI answered but human had to execute
- Project path confusion (SaaS-roams vs SaaS-O-Matic)

---

## Phase 2: Backend Implementation (Days 3-5)

### Approach
- Built models → schemas → validators → pricing → endpoints incrementally
- Tested each endpoint in Swagger UI before moving on

### AI Role
- Generated SQLAlchemy models, Pydantic schemas, FastAPI routes
- Spanish tax ID validation logic (DNI/NIE/CIF with check digits)
- Progressive pricing algorithm

### Critical Bugs Found & Fixed

| Bug | Root Cause | Fix |
|-----|------------|-----|
| 500 on GET /customers | Duplicate POST /customers route | Deleted duplicate, dropped DB, recreated |
| CIF validation rejects non-Spain | `field_validator` can't see `country` field | Switched to `model_validator(mode="after")` |
| `pydantic_core` ImportError | Corrupted venv after pip upgrades | `rm -rf venv && python -m venv venv` |
| FK constraint on delete customer | No cascade in relationship | Added `cascade="all, delete-orphan"` |

### Lessons
- **Test in Swagger UI every endpoint immediately** — catches 80% of bugs before frontend
- **Drop and recreate DB** when schema changes (SQLite dev mode)
- **Pydantic v2**: use `model_validator` for cross-field validation, not `field_validator`

---

## Phase 3: Frontend Implementation (Days 6-8)

### Approach
- React + TypeScript + Vite
- Built API service layer first (axios)
- Components: CustomerSearch → CustomerCard → SimulationPreview

### AI Role
- Component scaffolding, hooks, TypeScript types
- Toast notification system (hook + component)
- Currency conversion integration

### Critical Bugs Found & Fixed

| Bug | Root Cause | Fix |
|-----|------------|-----|
| "Cannot find module '../types'" | TS server cache | `Ctrl+Shift+P` → Restart TS Server |
| CORS 405 Method Not Allowed | Missing CORSMiddleware | Added to FastAPI `allow_origins=["http://localhost:3000"]` |
| Validation errors show `[object Object]` | FastAPI returns array, not string | `detail.map(e => e.msg).join(', ')` |
| Hook called outside component | `useState` at module level | Moved inside component function |
| `useEffect` missing dependency | `loadSimulations` not in deps | Wrapped in `useCallback`, added to deps |

### UX Decisions
- **Sliders in preview** (requirement: "slider or dynamic controls")
- **Number inputs in form** (precise entry)
- **Single source of truth** in CustomerCard — preview becomes controlled component
- **Toast notifications** replace native `alert()` — non-blocking, auto-dismiss

### Lessons
- **Restart TS Server** after adding new files/exports
- **Check Network tab** for CORS preflight (OPTIONS) failures
- **Parse FastAPI error format** — it's `{ detail: [{ msg, loc, type }] }`
- **Controlled components** prevent sync bugs between form and preview

---

## Phase 4: Integration & Polish (Days 9-10)

### Approach
- Connect all delete endpoints with confirmation dialogs
- Verify cascade delete works end-to-end
- Fix all ESLint/TS warnings
- Update documentation

### AI Role
- Code review (correctness, simplification)
- Bug fixes for remaining issues
- Documentation updates (development-log.md, this file)

### Critical Fixes

| Issue | Fix |
|-------|-----|
| Delete without confirmation | Added `window.confirm` to both simulation and customer delete |
| Preview/form desync | Made SimulationPreview controlled: receives values + callbacks from CustomerCard |
| ESLint `exhaustive-deps` warning | Added `fetchPreview` to useEffect deps (stable via useCallback) |
| Parsing error line 225 | Missing `}` in catch block — cascaded from earlier error |

### Lessons
- **Confirm before destructive actions** — UX 101, easy to skip
- **One source of truth** — eliminates entire class of sync bugs
- **ESLint false positives** — sometimes adding the dep to array is the pragmatic fix
- **Documentation lives with code** — update it when you fix things

---

## AI Interaction Patterns That Worked

### Good Prompts
- "Here's the spec, here's the current code, what's the minimal change to add X?"
- "This error: [paste]. The code is [paste]. What's the root cause and fix?"
- "Review this diff for correctness and simplification"

### Bad Prompts (Avoided)
- "Build the whole frontend" — too big, hallucinates
- "Fix it" — no context, generic fixes
- "Write tests" without specifying what to test

### Workflow
```
Human: Define task + constraints
AI:  Propose approach + files to change
Human: Review, approve, or redirect
AI:  Generate code changes
Human: Apply, test in browser/Swagger
AI:  Debug failures (with error logs)
Human: Verify, commit
```

---

## Metrics (Approximate)

| Metric | Value |
|--------|-------|
| Total dev time | ~10 days (part-time) |
| AI-assisted code | ~70% |
| Human-reviewed/edited | 100% |
| Bugs caught in Swagger/browser | ~15 |
| Bugs caught by AI review | ~5 |
| Files created/modified | ~25 |
| Documentation files | 8 |

---

## What I'd Do Differently Next Time

1. **Start with OpenAPI spec** — generate both backend routes and frontend types from single source
2. **Add E2E tests earlier** — Playwright/Cypress for critical flows (create customer → create sim → delete)
3. **Use stricter TypeScript** — `strict: true`, `noUncheckedIndexedAccess` from day 1
4. **Docker from start** — avoids "works on my machine" for backend deps
5. **Document decisions in real-time** — not retroactively

---

## Key Takeaways

- **AI is a force multiplier for known patterns** (CRUD, validation, standard React hooks)
- **AI struggles with cross-cutting concerns** (CORS, cascade delete, error format consistency) — human must connect the dots
- **The best debugging tool is the browser Network tab + Swagger UI** — not the AI
- **Vibe coding = human steering, AI rowing** — you still need to know where the boat is going
- **Documentation written during development > documentation written after**

---

*Last updated: 2025-01-17 — Implementation complete, docs finalized*