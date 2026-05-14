# AgroLens — Developer Setup

Complete guide to getting the stack running locally from a fresh clone.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x (running)
- Git
- A terminal (zsh / bash)

You do **not** need Python, Node, or any other runtime installed locally — everything runs inside Docker.

---

## 1. Clone and enter the repo

```bash
git clone https://github.com/dansxb/AgroLens.git
cd AgroLens/src
```

---

## 2. Set up environment files

Three `.env` files are required. Copy the examples and fill in your credentials:

```bash
# Root docker-compose env (Postgres + Redis passwords)
cp .env.example .env

# Backend (FastAPI, Celery, external APIs)
cp backend/.env.example backend/.env

# Frontend (Next.js public vars)
cp frontend/.env.example frontend/.env
```

### Credentials you need to fill in

| Variable(s) | Service | Where to get |
|-------------|---------|-------------|
| `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET` | [Supabase](https://supabase.com) | Project → Settings → API |
| `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase | Same page, anon/public key |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | [Mapbox](https://account.mapbox.com/access-tokens/) | Create access token |
| `SENTINEL_HUB_CLIENT_ID/SECRET/INSTANCE_ID` | [Sentinel Hub](https://apps.sentinel-hub.com/dashboard/) | Create service account |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME` | AWS S3 | IAM → create user |
| `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | [SendGrid](https://app.sendgrid.com) | Settings → API keys |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID_*` | [Stripe](https://dashboard.stripe.com) | Phase 5 — can skip for now |

**Minimum to get the UI running:** Supabase + Mapbox. All other credentials only block the specific features that use them.

> `SUPABASE_JWT_SECRET` is the raw signing secret (a plain string), **not** the service role JWT. Find it at Supabase → Settings → API → JWT Settings → JWT Secret.

---

## 3. Generate a SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output into `backend/.env` as `SECRET_KEY=...`.

---

## 4. Start the stack

```bash
docker compose up --build
```

Wait until all four services are healthy (takes 2–4 minutes on first build):

```
agrolens_postgres   healthy
agrolens_redis      healthy
agrolens_backend    Uvicorn running on http://0.0.0.0:8000
agrolens_frontend   ready - started server on 0.0.0.0:3000
```

---

## 5. Run database migrations (first time only)

In a second terminal:

```bash
cd AgroLens/src
docker compose exec backend alembic upgrade head
```

Expected output: `Running upgrade ... -> 0006, create_api_keys`

---

## 6. Verify everything is working

| URL | What you should see |
|-----|-------------------|
| http://localhost:3000 | AgroLens login/signup screen |
| http://localhost:8000/health | `{"status": "ok"}` |
| http://localhost:8000/docs | Swagger UI — all endpoints |

---

## Project structure

```
src/
├── backend/
│   ├── app/
│   │   ├── api/routes/         REST endpoints (fields, farms, prescriptions, etc.)
│   │   ├── core/               Config, DB session, auth, rate limiting
│   │   ├── models/             SQLAlchemy ORM models
│   │   ├── schemas/            Pydantic request/response schemas
│   │   ├── services/           Business logic (prescription, export, S3, Stripe)
│   │   └── worker/tasks/       Celery background tasks
│   ├── alembic/versions/       Database migrations (0001–0006)
│   ├── templates/email/        German HTML email templates (SendGrid)
│   ├── tests/                  Pytest test suite
│   ├── requirements.txt        Pinned Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── (auth)/             Login, signup, password reset pages
│   │   └── (dashboard)/        Dashboard, fields, settings, billing pages
│   ├── components/             React components (map, charts, forms, layout)
│   ├── lib/                    API client, Supabase helpers, Mapbox utilities
│   ├── hooks/                  useAuth and other custom hooks
│   ├── types/                  TypeScript type definitions
│   ├── package.json
│   └── Dockerfile
├── ml/
│   ├── indices/                NDVI + NDRE computation
│   ├── zones/                  K-means zone delineation
│   ├── prescription/           Application rate engine
│   ├── sentinel/               Sentinel Hub API client
│   ├── cloud_mask.py           Cloud masking for imagery
│   └── tests/                  ML module tests
├── infra/
│   ├── postgres/init.sql       PostGIS extension init
│   └── datadog/                Monitoring config
└── docker-compose.yml
```

---

## Common commands

```bash
# View logs for a service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery_worker

# Run a new migration after adding a model
docker compose exec backend alembic upgrade head

# Access the database directly
docker compose exec postgres psql -U agrolens -d agrolens_dev

# Restart a single service after a code change
docker compose restart backend

# Full reset — deletes all data and volumes
docker compose down -v && docker compose up --build

# Run backend tests
docker compose exec backend pytest tests/ -v

# Run ML tests
docker compose exec backend pytest ../ml/tests/ -v
```

---

## Database migrations

Migrations live in `backend/alembic/versions/`. Current state:

| Migration | What it creates |
|-----------|----------------|
| `0001` | users, farms, fields |
| `0002` | satellite_scenes, vegetation_indices, pipeline_runs |
| `0003` | FLIK field identifier |
| `0004` | management_zones, prescriptions, spraying_records |
| `0005` | notification_preferences |
| `0006` | api_keys |

To create a new migration:
```bash
docker compose exec backend alembic revision --autogenerate -m "describe_what_changes"
docker compose exec backend alembic upgrade head
```

---

## Feature availability by credentials

| Feature | Credentials needed |
|---------|-------------------|
| Login / signup | Supabase |
| Map renders | Mapbox |
| Field CRUD + dashboard | Supabase + Mapbox |
| API keys + rate limiting | None (works out of the box) |
| Satellite imagery fetch | Sentinel Hub |
| NDVI charts (real data) | Sentinel Hub + AWS S3 |
| Prescription maps + exports | Sentinel Hub + AWS S3 |
| Email notifications | SendGrid |
| Billing (Phase 5) | Stripe |

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Login returns 401 | Wrong `SUPABASE_JWT_SECRET` | Paste the raw signing secret, not a JWT token |
| Map is blank | Wrong `NEXT_PUBLIC_MAPBOX_TOKEN` | Check the token at mapbox.com |
| `alembic upgrade` fails | Postgres not ready | Wait 30s and retry |
| Backend crashes on start | Missing env var or import error | `docker compose logs backend` |
| Frontend blank page | Compile error | `docker compose logs frontend` |
| `rasterio` build fails | Missing GDAL system libs | Already handled in Dockerfile — rebuild with `--no-cache` |

---

## Docker build notes

The backend Dockerfile uses `--no-build-isolation` for `rasterio` to work around a pip 26 isolated build environment bug. If you see `No module named pkg_resources`, ensure `setuptools` is installed before the main `pip install`:

```dockerfile
RUN pip install "setuptools<81" pip --upgrade && \
    pip install --no-build-isolation -r requirements.txt
```
