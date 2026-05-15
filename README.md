# AgroLens

Precision agriculture SaaS for German farmers. Pulls Sentinel-2 satellite imagery daily, computes NDVI/NDRE vegetation indices, delineates management zones via k-means clustering, and generates Variable Rate Application (VRA) prescription maps as ISOBUS-compatible TASKDATA.XML, Shapefile, and PDF exports.

**Core value proposition:** Reduce pesticide use by 20–40% through satellite-driven prescription maps.

---

## Repository layout

```
├── src/                    Application code (start here)
│   ├── backend/            FastAPI + SQLAlchemy + Celery
│   ├── frontend/           Next.js 14 + Tailwind + Mapbox GL JS
│   ├── ml/                 Vegetation indices, zone delineation, prescription engine
│   ├── infra/              Postgres init SQL, Datadog config
│   ├── docker-compose.yml  Full local stack (Postgres, Redis, backend, frontend, Celery)
│   ├── .env.example        Root docker-compose env vars (copy → .env)
│   └── README.md           Developer quickstart
├── .claude/agents/         AI agent definitions (CEO, planner, developer, checker, etc.)
├── docs/                   Architecture decisions, dev log, checker reviews
├── obsidian/               Obsidian knowledge vault — architecture, ADRs, phase boards
│   ├── Home.md             Start here for project overview
│   ├── Architecture/       System overview, data model, ML pipeline, API endpoints
│   ├── Tasks/              Phase task boards
│   └── Dev Setup/          Environment setup + first test guide
└── tasks/                  Claude task tracking (todo.md, lessons.md)
```

---

## Quickstart

See **[src/README.md](src/README.md)** for the full developer setup guide.

**TL;DR — three commands after copying your `.env` files:**

```bash
cd src
docker compose up --build
docker compose exec backend alembic upgrade head   # first run only
```

Then open [http://localhost:3000](http://localhost:3000).

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI, SQLAlchemy 2 (async), Alembic |
| Database | PostgreSQL 15 + PostGIS 3.x |
| Background tasks | Celery 5 + Redis 7 |
| Frontend | Next.js 14, Tailwind CSS, Mapbox GL JS, Recharts |
| Auth | Supabase (JWT + email/Google OAuth) |
| Satellite imagery | Sentinel Hub API (Copernicus Sentinel-2 L2A) |
| ML | scikit-learn k-means, NumPy, rasterio |
| Storage | AWS S3 (imagery + exports) |
| Billing | Stripe Subscriptions |
| Email | SendGrid |
| Error tracking | Sentry |

---

## Phase status

| Phase | What was built | Status |
|-------|---------------|--------|
| 0 | Docker, Postgres+PostGIS, Redis, Alembic baseline | ✅ Done |
| 1 | User/Farm/Field models, Supabase JWT auth, API key auth, rate limiting | ✅ Done |
| 2 | Sentinel-2 imagery pipeline, NDVI/NDRE computation, cloud masking, S3 storage | ✅ Done |
| 3 | k-means zone delineation, prescription engine, Shapefile/TASKDATA.XML/PDF exports | ✅ Done |
| 4 | Dashboard UI (Mapbox, Recharts), field CRUD, notification preferences, API keys, PWA | ✅ Done |
| **5** | **Stripe billing, subscription model, plan enforcement** | **Next** |

---

## Credentials needed

Before you can run the stack you need credentials for six external services. All go into `.env` files — templates are provided as `.env.example` in each directory.

| Service | What for | Where to get |
|---------|---------|-------------|
| [Supabase](https://supabase.com) | Auth (JWT + user management) | Project dashboard → Settings → API |
| [Sentinel Hub](https://apps.sentinel-hub.com/dashboard/) | Satellite imagery | Create service account → OAuth2 credentials |
| [AWS S3](https://aws.amazon.com/s3/) | Imagery + export file storage | IAM → create user with S3 permissions |
| [Mapbox](https://account.mapbox.com/access-tokens/) | Map rendering in frontend | Create access token |
| [SendGrid](https://app.sendgrid.com/settings/api_keys) | Transactional email | Create API key |
| [Stripe](https://dashboard.stripe.com/apikeys) | Billing (Phase 5) | Test keys from dashboard |

---

## Knowledge base (Obsidian)

The `obsidian/` directory is an [Obsidian](https://obsidian.md) vault. Open it with Obsidian to browse architecture decision records (ADRs), the full API endpoint reference, data model diagrams, and phase-by-phase dev logs.

Key files:
- [`obsidian/Home.md`](obsidian/Home.md) — top-level index
- [`obsidian/Architecture/System Overview.md`](obsidian/Architecture/System%20Overview.md) — services, data flow
- [`obsidian/Architecture/API Endpoints.md`](obsidian/Architecture/API%20Endpoints.md) — full REST reference
- [`obsidian/Tasks/Phase 5 Board.md`](obsidian/Tasks/Phase%205%20Board.md) — what's being built next
- [`obsidian/Dev Setup/Environment Setup.md`](obsidian/Dev%20Setup/Environment%20Setup.md) — credentials checklist

---

## AI agent team

The `.claude/agents/` directory contains agent definition files for [Claude Code](https://claude.ai/code). Each agent has a focused role:

| Agent | Role |
|-------|------|
| `ceo.md` | Market research, strategy, competitor analysis |
| `planner.md` | Translates strategy into structured dev tasks |
| `software-developer.md` | Implements backend, frontend, ML modules |
| `checker.md` | Code review, security, GDPR/§67 PflSchG compliance |
| `landwirt-validator.md` | Agricultural correctness, ISOBUS compatibility |
| `debug-spezialist.md` | Targeted bug diagnosis (spawned on-demand) |

---

## Regulatory context

- **§67 PflSchG** — German pesticide law mandates documentation of every application → `SprayingRecord` model
- **FLIK-Nummer** — German field identifier for EU cross-compliance (InVeKoS)
- **ISOBUS ISO 11783-10** — Shapefile alone is not compatible with tractor terminals; TASKDATA.XML is mandatory
- **DSGVO / GDPR** — Farmer field data stored in EU regions only (S3: `eu-central-1`)

---

## Running tests

Tests that need only NumPy/pure Python can run locally:

```bash
# Activate the agrolens conda env (or use pip install pytest numpy)
conda activate agrolens

# ML unit tests (NDVI/NDRE formulas, cloud masking, compositing)
PYTHONPATH=src/backend:src python -m pytest src/ml/tests/test_indices.py -v

# Prescription engine tests
PYTHONPATH=src/backend:src python -m pytest src/backend/tests/test_prescription_engine.py -v
```

Tests that require a live database or Sentinel Hub must run inside Docker:

```bash
cd src
docker compose exec backend pytest tests/test_auth.py tests/test_fields_api.py -v
docker compose exec backend pytest ../ml/tests/test_delineation.py -v
```

---

## Environment variables

All env vars are documented in `src/.env.example`. The most critical ones:

| Variable | Where used |
|----------|-----------|
| `SUPABASE_URL` + `SUPABASE_JWT_SECRET` | Backend JWT verification |
| `NEXT_PUBLIC_SUPABASE_URL` + `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend Supabase client |
| `SENTINEL_HUB_CLIENT_ID` + `SENTINEL_HUB_CLIENT_SECRET` | Imagery pipeline |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `S3_BUCKET` | File storage |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | Map rendering |
| `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL` | Transactional email |
| `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` | Billing (Phase 5) |
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend error tracking (optional) |

---

## Contributing

1. Branch from `main` — naming: `feat/`, `fix/`, `refactor/`, `docs/`
2. Run `black src/backend src/ml` and `isort src/backend src/ml --profile black` before committing
3. All local tests must pass (`pytest` commands above)
4. Any prescription rate change requires updating the multiplier table docstring in `src/ml/prescription/engine.py` and the agronomist sign-off comment
