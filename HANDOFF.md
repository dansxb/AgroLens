# AgroLens — Session Handoff

*Claude reads this at every session start. Last updated: 2026-05-14.*

---

## What this project is

AgroLens is a precision agriculture SaaS for German farmers. It pulls Sentinel-2 satellite imagery, computes NDVI/NDRE vegetation indices, runs k-means clustering to delineate management zones, and generates Variable Rate Application (VRA) prescription maps. Output: ISOBUS-compatible TASKDATA.XML + Shapefile exports, PDF reports, email alerts.

**Owner:** Daniel Schaller — communicates in German about product, English for technical work. Prefers concise responses, no trailing summaries.

---

## Phase status

| Phase | What was built | Status |
|---|---|---|
| 0 | Docker, Postgres+PostGIS, Redis, Alembic baseline | ✅ Done |
| 1 | User/Farm/Field models, Supabase JWT auth, API key auth, rate limiting | ✅ Done |
| 2 | Sentinel-2 imagery pipeline, NDVI/NDRE computation, cloud masking, S3 storage | ✅ Done |
| 3 | k-means zone delineation, prescription engine, Shapefile/TASKDATA.XML/PDF exports | ✅ Done |
| 4 | Dashboard UI (Mapbox, Recharts), field CRUD, notification preferences, API keys, PWA | ✅ Done |
| **5** | **Stripe billing, subscription model, plan enforcement** | **🔲 Next** |

---

## Phase 5 — what to build next

**Backend:**
- `Subscription` ORM model (PgEnum: **basis/starter/farmer/pro**/trialing/past_due/canceled — `create_type=False`)
- Migration `0007_create_subscriptions.py`
- `services/stripe_service.py` — create_checkout_session, create_portal_session, get_or_create_customer
- `POST /api/v1/billing/checkout` and `POST /api/v1/billing/portal`
- `POST /api/v1/webhooks/stripe` — verify Stripe-Signature, handle 5 webhook events, update Subscription
- `app/core/limits.py` — **basis: 1 field/15 ha (free, no export)**, starter: 5 fields/**100 ha**, farmer: 50 fields/500 ha, pro: unlimited
- Enforce limits in `POST /api/v1/fields` and `POST /api/v1/fields/{id}/prescriptions`
- Update `GET /api/v1/account/usage` to return real plan_limit from Subscription

**Pricing (updated 2026-05-14):**
- Basis: €0 (permanent free tier — 1 field, 15 ha, NDVI only, no export)
- Starter: €49/mo · €470/yr — 5 fields, 100 ha
- Farmer: €149/mo · €1.430/yr — 50 fields, 500 ha (recommended)
- Pro: **€599/mo · €5.750/yr** — unlimited (raised from €399 — Lohnunternehmer pricing)

**Frontend:**
- `app/(dashboard)/settings/billing/page.tsx`
- Checkout redirect flow
- Subscription status banner (past_due/canceled)
- Upgrade CTA from PlanUsageBar

**Note:** `db/base.py` has a `try/except` guard for the Phase 5 Subscription import — remove it once the model is implemented.

---

## File paths

| What | Path |
|---|---|
| Project root | `/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/` |
| Source code | `src/` |
| Backend | `src/backend/` |
| Frontend | `src/frontend/` |
| ML pipeline | `src/ml/` |
| Docker Compose | `src/docker-compose.yml` |
| Backend .env | `src/backend/.env` |
| Frontend .env | `src/frontend/.env` |
| Agent definitions | `.claude/agents/` (ceo, planner, software-developer, checker, landwirt-validator) |
| Obsidian vault | `/Users/danielschaller/Documents/AgroLens/` |
| Claude memory | `~/.claude/projects/-Users-danielschaller-Desktop-CS-Haus---Garten-Winter--Claude-Agents/memory/` |
| Tasks | `tasks/todo.md`, `tasks/lessons.md` |
| Docs | `docs/` (ceo-strategy, development-plan, checker-review, landwirt-validator-report, dev-log, blockers) |

---

## Credentials status (src/backend/.env)

| Variable | Status |
|---|---|
| SECRET_KEY | ✅ set (64-char hex) |
| SUPABASE_URL | ✅ `https://feoohtmphywquwzonpwq.supabase.co` |
| SUPABASE_SERVICE_ROLE_KEY | ✅ set |
| SUPABASE_JWT_SECRET | ✅ set (base64 signing key) |
| NEXT_PUBLIC_SUPABASE_URL | ✅ set (frontend/.env) |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | ✅ set (frontend/.env) |
| NEXT_PUBLIC_MAPBOX_TOKEN | ✅ set (frontend/.env) |
| SENTINEL_HUB_* | ❌ missing — imagery pipeline won't work |
| AWS_* | ❌ missing — S3 storage/exports won't work |
| SENDGRID_API_KEY | ❌ missing — email notifications won't work |
| STRIPE_* | ❌ missing — needed for Phase 5 |

---

## Agent team

Six agents. **Every phase needs Checker + Landwirt Validator approval before marking complete.**

| Agent | Role | Writes to |
|---|---|---|
| `ceo` | Market research, strategy, goals | `docs/ceo-strategy.md` |
| `planner` | Translates CEO goals → dev tasks | `docs/development-plan.md` |
| `software-developer` | Implements everything | code + `docs/dev-log.md` |
| `checker` | Code quality, security, architecture review | `docs/checker-review.md` |
| `landwirt-validator` | German farmer workflow, §67 PflSchG, ISOBUS review | `docs/landwirt-validator-report.md` |
| `debug-spezialist` | Root-cause bug fixer — on-demand only | `docs/debug-log.md` |

**Phase gate:** Checker = APPROVED **and** Landwirt Validator = FREIGEGEBEN → phase complete.

**Debug escalation:** When a specific error (traceback, 5xx, build failure) blocks progress, spawn `debug-spezialist` with the full error text. It diagnoses, fixes, verifies, and documents in `docs/debug-log.md`.

---

## Critical rules (hard-learned, never break these)

### Python / SQLAlchemy
```python
# ALWAYS PgEnum — NEVER sa.Enum (causes DuplicateObject on migration rerun)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
MY_ENUM = PgEnum("a", "b", name="mytype", create_type=False)

# relationship() has NO comment= kwarg (TypeError at import)
user = relationship("User")  # ✅   relationship("User", comment="x")  # ❌

# DB dependency name
from app.db.session import get_db   # ✅   get_async_db does NOT exist

# Model field: VegetationIndex.created_at  (NOT computed_at)
# Celery workers: use sync SessionLocal, not AsyncSessionLocal
```

### Frontend / TypeScript
```typescript
import * as toGeoJSON from "@mapbox/togeojson"  // ✅ — named import breaks
// next-pwa v5: no require("next-pwa/cache") sub-path
```

### Docker / Dockerfile
```dockerfile
# setuptools<81 required — 81+ removes pkg_resources from isolated build envs
# rasterio 1.3.x has no ARM64 wheel → always builds from source → needs pkg_resources
RUN pip install "setuptools<81" pip --upgrade && \
    pip install --prefix=/install -r requirements.txt

# Builder stage needs: libgdal-dev libgeos-dev libproj-dev gdal-bin
```

### Alembic migrations
- PostGIS geometry columns: use `op.execute("SELECT AddGeometryColumn(...)")` — never inline
- Every migration must have `revision`, `down_revision`, `upgrade()`, `downgrade()`
- Geometry columns need a GIST spatial index

### Workflow
- Plan mode for any task with 3+ steps
- Read every file before Write (Write fails on unread files)
- Never mark task complete without verifying it works
- Update Obsidian vault at end of session

---

## Local environment

| Tool | Command |
|---|---|
| Activate Python env | `conda activate agrolens` |
| Python interpreter | `/opt/anaconda3/envs/agrolens/bin/python` (Python 3.11, matches Docker) |
| Start stack | `cd src && docker compose up --build` |
| Run migrations | `docker compose exec backend alembic upgrade head` |
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

---

## Obsidian vault (`/Users/danielschaller/Documents/AgroLens/`)

Auto-loaded at every session start via `~/.claude/settings.json` SessionStart hook.

Key files:
- `Memory/Context.md` — project state + key rules (keep updated)
- `Memory/Quick Reference.md` — dense lookup: import rules, env vars, model fields, docker commands
- `Memory/Session Changes.md` — auto-populated by PostToolUse hook when files are written
- `Tasks/Phase 5 Board.md` — open task checklist
- `Architecture/Decisions/` — ADR-001 through ADR-005 (why things were built a certain way)
- `Agents/` — research docs for each agent
- `Dev Log/` — one entry per session

---

## Migrations in order

0001 → users/farms/fields + PostGIS  
0002 → imagery pipeline tables  
0003 → flik column on fields  
0004 → management zones, prescriptions, spraying records  
0005 → notification preferences  
0006 → api keys  
0007 → subscriptions (Phase 5, not yet built)
