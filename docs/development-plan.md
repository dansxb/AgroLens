# AgroLens — Complete MVP Development Plan
**Version 1.0 | Prepared: 2026-05-11 | Author: Planner Agent**

---

## Overview

This plan translates the 5 strategic goals and 16 MVP requirements from the CEO strategy document into a dependency-aware, phase-by-phase development roadmap. Each task is self-contained, assigned to the Software Developer, and scoped so that no two concurrent tasks modify the same file.

### Strategic Goals Addressed

| Goal | Addressed by Phases |
|---|---|
| Goal 1: Ship MVP with 10 paid pilot farms | All phases |
| Goal 2: Functioning AI/ML pipeline for VRA map generation | Phases 2 & 3 |
| Goal 3: Cooperative distribution partner (CEO-owned, but platform must be demo-ready) | Phases 0–4 |
| Goal 4: Seed funding (CEo-owned, but working demo required) | Phases 0–2 |
| Goal 5: Validate ROI story with pilot data | Phases 3 & 4 |

### Requirements Cross-Reference

| Requirement | Primary Phase | Task(s) |
|---|---|---|
| REQ-01: Field Boundary Management | Phase 1 & 4 | 1.3, 4.1 |
| REQ-02: Sentinel-2 Imagery Retrieval | Phase 2 | 2.1, 2.2 |
| REQ-03: Vegetation Index Computation | Phase 2 | 2.3 |
| REQ-04: Management Zone Delineation | Phase 3 | 3.1 |
| REQ-05: VRA Prescription Map Generation | Phase 3 | 3.2 |
| REQ-06: Shapefile Export | Phase 3 | 3.3 |
| REQ-07: Farmer Dashboard — Field Overview | Phase 4 | 4.2 |
| REQ-08: Field Detail View | Phase 4 | 4.3 |
| REQ-09: Notifications | Phase 4 | 4.5 |
| REQ-10: Mobile-Responsive Design | Phase 4 | 4.4 |
| REQ-11: Authentication & Account Management | Phase 1 | 1.1, 1.2 |
| REQ-12: Subscription Billing | Phase 5 | 5.1, 5.2 |
| REQ-13: REST API (MVP scope) | Phase 3 & 4 | 3.2, 4.6 |
| REQ-14: Infrastructure Architecture | Phase 0 | 0.1–0.4 |
| REQ-15: Security & Compliance | Phase 1 | 1.4 |
| REQ-16: Monitoring & Alerting | Phase 5 | 5.3 |

---

## Phase 0: Project Foundation

**Goal:** Establish the full monorepo skeleton, Docker-based local development environment, secrets management, and application skeletons so that all subsequent phases begin with a running, health-checked system.

**Dependencies:** None — this phase has no upstream dependencies.

---

### Task 0.1: Monorepo Directory Structure & Git Initialization

- **What**: Initialize the monorepo with the canonical top-level directory layout: `backend/`, `frontend/`, `ml/`, `infra/`, `docs/`. Create a root-level `.gitignore` covering all secrets files, Python cache artifacts, Node.js artifacts, build outputs, and IDE files. Create a root `README.md` with local setup instructions, required tool versions, and a quickstart guide.
- **Files to create/modify**:
  - `.gitignore`
  - `README.md`
  - `backend/.gitkeep`
  - `frontend/.gitkeep`
  - `ml/.gitkeep`
  - `infra/.gitkeep`
  - `docs/.gitkeep`
- **Depends on**: none
- **Acceptance criteria**:
  - Running `git status` from repo root shows no untracked secrets files (.env, *.pem, *.key)
  - `.gitignore` explicitly covers: `**/.env`, `**/__pycache__`, `**/node_modules`, `**/.next`, `**/dist`, `**/*.pyc`, `**/.DS_Store`, `**/venv`, `**/.venv`, `**/coverage`, `**/*.egg-info`, `**/build`
  - `README.md` contains sections: Prerequisites, Quick Start (clone → docker-compose up), Environment Variables, Project Structure, Running Tests
  - All five top-level directories exist and are committed
- **Tech**: Git, Markdown
- **Assigned to**: Software-Developer

---

### Task 0.2: Secrets & Environment Variables Specification

- **What**: Create `.env.example` files for both backend and frontend that enumerate every environment variable required across the entire project (all phases). Each variable must have an inline comment explaining its purpose, where to obtain its value, and whether it is required or optional. Also create a root-level `.env.example` for docker-compose overrides.
- **Files to create/modify**:
  - `backend/.env.example`
  - `frontend/.env.example`
  - `.env.example` (root, for docker-compose)
- **Depends on**: Task 0.1
- **Acceptance criteria**:
  - `backend/.env.example` contains all of the following variables with comments:
    - `DATABASE_URL` — PostgreSQL connection string with PostGIS
    - `SECRET_KEY` — FastAPI signing secret (32+ char random string)
    - `SUPABASE_URL` — Supabase project URL
    - `SUPABASE_SERVICE_ROLE_KEY` — Supabase service role key (server-side only)
    - `SUPABASE_JWT_SECRET` — JWT verification secret from Supabase dashboard
    - `SENTINEL_HUB_CLIENT_ID` — Sentinel Hub OAuth2 client ID
    - `SENTINEL_HUB_CLIENT_SECRET` — Sentinel Hub OAuth2 client secret
    - `SENTINEL_HUB_INSTANCE_ID` — Sentinel Hub instance/configuration ID
    - `AWS_ACCESS_KEY_ID` — AWS credentials for S3 access
    - `AWS_SECRET_ACCESS_KEY` — AWS credentials for S3 access
    - `AWS_S3_BUCKET_NAME` — S3 bucket for imagery and export storage
    - `AWS_S3_REGION` — AWS region (must be EU region: eu-west-1 or eu-central-1)
    - `STRIPE_SECRET_KEY` — Stripe secret key (sk_live_... or sk_test_...)
    - `STRIPE_WEBHOOK_SECRET` — Stripe webhook signing secret
    - `STRIPE_PRICE_ID_STARTER_MONTHLY` — Stripe Price ID for Starter monthly plan
    - `STRIPE_PRICE_ID_STARTER_ANNUAL` — Stripe Price ID for Starter annual plan
    - `STRIPE_PRICE_ID_FARMER_MONTHLY` — Stripe Price ID for Farmer monthly plan
    - `STRIPE_PRICE_ID_FARMER_ANNUAL` — Stripe Price ID for Farmer annual plan
    - `STRIPE_PRICE_ID_PRO_MONTHLY` — Stripe Price ID for Pro monthly plan
    - `STRIPE_PRICE_ID_PRO_ANNUAL` — Stripe Price ID for Pro annual plan
    - `SENDGRID_API_KEY` — SendGrid API key for transactional email
    - `SENDGRID_FROM_EMAIL` — Verified sender email address
    - `ENVIRONMENT` — One of: development, staging, production
    - `ALLOWED_ORIGINS` — Comma-separated CORS origins
    - `LOG_LEVEL` — Python logging level (DEBUG, INFO, WARNING, ERROR)
    - `CELERY_BROKER_URL` — Redis or RabbitMQ URL for background task queue
    - `CELERY_RESULT_BACKEND` — Celery result backend URL
    - `SENTRY_DSN` — Sentry DSN for error tracking (backend)
  - `frontend/.env.example` contains all of the following with comments:
    - `NEXT_PUBLIC_API_BASE_URL` — Base URL of the FastAPI backend
    - `NEXT_PUBLIC_SUPABASE_URL` — Supabase project URL (public, safe to expose)
    - `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Supabase anon/public key
    - `NEXT_PUBLIC_MAPBOX_TOKEN` — Mapbox GL JS access token
    - `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` — Stripe publishable key
    - `NEXT_PUBLIC_SENTRY_DSN` — Sentry DSN for frontend error tracking
    - `NEXT_PUBLIC_ENVIRONMENT` — One of: development, staging, production
  - Root `.env.example` contains docker-compose overrides: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `REDIS_PASSWORD`
  - No `.env.example` file contains any real secrets — all values are placeholder strings like `your_value_here` or `sk_test_replace_me`
- **Tech**: Shell, dotenv convention
- **Assigned to**: Software-Developer

---

### Task 0.3: Docker & docker-compose Local Development Environment

- **What**: Create a `docker-compose.yml` at the repo root that orchestrates all local development services: PostgreSQL 15 with PostGIS extension, Redis (for Celery broker), the FastAPI backend, and the Next.js frontend. Create a `Dockerfile` for the backend and a `Dockerfile` for the frontend. All services must start with a single `docker-compose up` command. Include a `docker-compose.override.yml.example` for developer-specific overrides. Create an `infra/postgres/init.sql` script that enables the PostGIS extension on first startup.
- **Files to create/modify**:
  - `docker-compose.yml`
  - `docker-compose.override.yml.example`
  - `backend/Dockerfile`
  - `frontend/Dockerfile`
  - `infra/postgres/init.sql`
- **Depends on**: Task 0.1
- **Acceptance criteria**:
  - `docker-compose up` from repo root starts all four services without errors
  - PostgreSQL is reachable at `localhost:5432` with PostGIS extension installed (verified by `SELECT PostGIS_Version();`)
  - Redis is reachable at `localhost:6379`
  - Backend health check endpoint responds at `http://localhost:8000/health` with `{"status": "ok"}`
  - Frontend dev server responds at `http://localhost:3000`
  - Volume mounts configured so code changes in `backend/` and `frontend/` are hot-reloaded without container restart
  - `backend/Dockerfile` uses Python 3.11-slim base image, installs GDAL system dependencies needed by rasterio and geopandas
  - `frontend/Dockerfile` uses Node 20-alpine base image
  - `infra/postgres/init.sql` runs `CREATE EXTENSION IF NOT EXISTS postgis;` and `CREATE EXTENSION IF NOT EXISTS postgis_topology;`
- **Tech**: Docker, docker-compose, PostgreSQL 15, PostGIS 3.x, Redis 7
- **Assigned to**: Software-Developer

---

### Task 0.4: Backend FastAPI Application Skeleton

- **What**: Create the FastAPI application skeleton inside `backend/`. This includes the main `app/` package, configuration loading via python-dotenv, a health check router, the root `main.py` entrypoint, and `requirements.txt` with all required Python dependencies pinned to specific versions. The skeleton must be structured for expansion: routers in `app/api/routes/`, shared dependencies in `app/api/deps.py`, database session management in `app/db/session.py`, and settings in `app/core/config.py`.
- **Files to create/modify**:
  - `backend/main.py`
  - `backend/requirements.txt`
  - `backend/app/__init__.py`
  - `backend/app/core/__init__.py`
  - `backend/app/core/config.py`
  - `backend/app/api/__init__.py`
  - `backend/app/api/deps.py`
  - `backend/app/api/routes/__init__.py`
  - `backend/app/api/routes/health.py`
  - `backend/app/db/__init__.py`
  - `backend/app/db/session.py`
- **Depends on**: Task 0.3
- **Acceptance criteria**:
  - `GET /health` returns `{"status": "ok", "environment": "<value of ENVIRONMENT env var>", "version": "0.1.0"}` with HTTP 200
  - `GET /health/db` returns `{"status": "ok", "database": "connected"}` when PostgreSQL is reachable, or `{"status": "error", "database": "unreachable"}` with HTTP 503 when not
  - `app/core/config.py` uses `pydantic-settings` `BaseSettings` to load all environment variables from Task 0.2 with type validation and defaults
  - CORS middleware configured to allow origins from `ALLOWED_ORIGINS` env var
  - Application runs via `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
  - `requirements.txt` pins: `fastapi==0.111.*`, `uvicorn[standard]==0.29.*`, `sqlalchemy==2.0.*`, `geoalchemy2==0.15.*`, `alembic==1.13.*`, `psycopg2-binary==2.9.*`, `pydantic-settings==2.2.*`, `python-dotenv==1.0.*`, `python-jose[cryptography]==3.3.*`, `passlib[bcrypt]==1.7.*`, `celery[redis]==5.3.*`, `rasterio==1.3.*`, `geopandas==0.14.*`, `numpy==1.26.*`, `scikit-learn==1.4.*`, `torch==2.2.*`, `sentinelhub==3.10.*`, `boto3==1.34.*`, `stripe==8.9.*`, `sendgrid==6.11.*`, `sentry-sdk[fastapi]==1.45.*`, `httpx==0.27.*`, `shapely==2.0.*`, `pyproj==3.6.*`
- **Tech**: FastAPI, Python 3.11, pydantic-settings, python-dotenv
- **Assigned to**: Software-Developer

---

### Task 0.5: Database SQLAlchemy Base & Alembic Setup

- **What**: Configure SQLAlchemy 2.0 async engine and declarative base for all future ORM models. Initialize Alembic for database migrations with the correct configuration pointing at the PostgreSQL+PostGIS database. Create the initial (empty) migration that records the baseline schema state.
- **Files to create/modify**:
  - `backend/app/db/base.py`
  - `backend/app/db/base_class.py`
  - `backend/alembic.ini`
  - `backend/alembic/env.py`
  - `backend/alembic/script.py.mako`
  - `backend/alembic/versions/.gitkeep`
- **Depends on**: Task 0.4
- **Acceptance criteria**:
  - `alembic upgrade head` from `backend/` directory completes without error against the running PostgreSQL container
  - `alembic downgrade -1` from `backend/` directory completes without error
  - `app/db/base_class.py` defines a `Base` class with `__tablename__` auto-derived from the class name (snake_case)
  - `app/db/session.py` provides both a synchronous `SessionLocal` for background tasks and an async `AsyncSessionLocal` for FastAPI route handlers
  - `alembic/env.py` imports `Base` from `app.db.base` so all models registered on `Base.metadata` are auto-detected during `alembic revision --autogenerate`
  - Alembic `sqlalchemy.url` reads from the `DATABASE_URL` environment variable, not hardcoded
- **Tech**: SQLAlchemy 2.0, Alembic 1.13, PostgreSQL 15, PostGIS
- **Assigned to**: Software-Developer

---

### Task 0.6: Frontend Next.js 14 Application Skeleton

- **What**: Scaffold the Next.js 14 application in `frontend/` using the App Router. Configure TypeScript in strict mode, Tailwind CSS, and the base project layout: root layout with metadata, a global CSS file importing Tailwind directives, and a simple homepage placeholder. Configure `next.config.js` for environment variable exposure and image optimization.
- **Files to create/modify**:
  - `frontend/package.json`
  - `frontend/tsconfig.json`
  - `frontend/next.config.js`
  - `frontend/tailwind.config.ts`
  - `frontend/postcss.config.js`
  - `frontend/app/layout.tsx`
  - `frontend/app/page.tsx`
  - `frontend/app/globals.css`
  - `frontend/public/.gitkeep`
  - `frontend/components/.gitkeep`
  - `frontend/lib/.gitkeep`
  - `frontend/types/.gitkeep`
- **Depends on**: Task 0.3
- **Acceptance criteria**:
  - `npm run dev` from `frontend/` starts the dev server on port 3000 without TypeScript errors
  - `npm run build` completes without errors
  - TypeScript `strict: true` is set in `tsconfig.json`
  - Tailwind is configured with a custom color palette including `agrolens` brand colors: `green-600` as primary, `amber-500` as warning, `red-500` as alert
  - Homepage at `/` renders the placeholder: "AgroLens — Precision Pesticide Intelligence" with the Tailwind green primary color
  - `next.config.js` exposes all `NEXT_PUBLIC_*` env vars and configures `images.domains` for Mapbox and Supabase storage
  - `package.json` dependencies include: `next@14.*`, `react@18.*`, `react-dom@18.*`, `typescript@5.*`, `tailwindcss@3.*`, `@supabase/supabase-js@2.*`, `@supabase/auth-helpers-nextjs@0.10.*`, `mapbox-gl@3.*`, `@types/mapbox-gl@3.*`, `recharts@2.*`, `@stripe/stripe-js@3.*`, `sentry/nextjs@7.*`, `lucide-react@0.376.*`, `clsx@2.*`, `zod@3.*`, `react-hook-form@7.*`, `@hookform/resolvers@3.*`
- **Tech**: Next.js 14, TypeScript 5, Tailwind CSS 3, App Router
- **Assigned to**: Software-Developer

---

## Phase 1: Core Data Models & Auth

**Goal:** Implement the full user authentication flow (Supabase Auth), the Farm and Field data models with PostGIS geometry support, database migrations, JWT-protected API route middleware, and the frontend login/signup pages.

**Dependencies:** All Phase 0 tasks must be complete.

---

### Task 1.1: User & Auth Models + Supabase Integration (Backend)

- **What**: Create the `User` SQLAlchemy model that mirrors Supabase Auth users (using the Supabase user UUID as primary key). Create the FastAPI JWT verification middleware that validates Supabase-issued JWTs on all protected routes. Implement the `get_current_user` dependency used by all authenticated endpoints.
- **Files to create/modify**:
  - `backend/app/models/__init__.py`
  - `backend/app/models/user.py`
  - `backend/app/core/security.py`
  - `backend/app/api/deps.py`
- **Depends on**: Task 0.5
- **Acceptance criteria**:
  - `User` model has columns: `id` (UUID, PK, matches Supabase user ID), `email` (string, unique, not null), `full_name` (string, nullable), `farm_name` (string, nullable), `country` (string(2), nullable, ISO 3166-1 alpha-2), `phone` (string, nullable), `stripe_customer_id` (string, nullable), `created_at` (datetime with timezone, server default now), `updated_at` (datetime with timezone, onupdate now)
  - `app/core/security.py` implements `verify_supabase_jwt(token: str) -> dict` that validates the JWT signature using `SUPABASE_JWT_SECRET`, checks expiry, and returns the decoded payload; raises `HTTPException(401)` on failure
  - `app/api/deps.py` implements `get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User` that calls `verify_supabase_jwt`, looks up or creates the user record, and returns it
  - All tests in `backend/tests/test_auth.py` pass: test valid JWT returns user, test expired JWT returns 401, test malformed JWT returns 401
- **Tech**: FastAPI, SQLAlchemy 2.0, python-jose, Supabase Auth
- **Assigned to**: Software-Developer

---

### Task 1.2: Farm & Field Models (Backend)

- **What**: Create `Farm` and `Field` SQLAlchemy models with PostGIS geometry column for field boundaries. `Farm` belongs to a `User`. `Field` belongs to a `Farm` and stores a polygon geometry in EPSG:4326. Implement automatic hectare area calculation via a PostGIS trigger or SQLAlchemy event listener.
- **Files to create/modify**:
  - `backend/app/models/farm.py`
  - `backend/app/models/field.py`
- **Depends on**: Task 1.1
- **Acceptance criteria**:
  - `Farm` model has columns: `id` (UUID, PK), `user_id` (UUID, FK → users.id, cascade delete), `name` (string, not null), `created_at`, `updated_at`
  - `Field` model has columns: `id` (UUID, PK), `farm_id` (UUID, FK → farms.id, cascade delete), `name` (string, not null), `crop_type` (enum: wheat/rapeseed/barley/maize/soybeans), `planting_date` (date, nullable), `geometry` (Geometry(Polygon, srid=4326) via GeoAlchemy2), `area_ha` (numeric(10,1), computed), `created_at`, `updated_at`
  - `area_ha` is automatically computed from `geometry` using PostGIS `ST_Area(ST_Transform(geometry, 3857)) / 10000` and kept up to date on geometry update
  - Both models are imported in `backend/app/db/base.py` so Alembic detects them
  - Field area displayed to 1 decimal place matches PostGIS computation
- **Tech**: SQLAlchemy 2.0, GeoAlchemy2, PostGIS, PostgreSQL 15
- **Assigned to**: Software-Developer

---

### Task 1.3: Alembic Migration — Users, Farms, Fields

- **What**: Generate and finalize the Alembic migration that creates the `users`, `farms`, and `fields` tables, including the PostGIS geometry column and the area computation logic.
- **Files to create/modify**:
  - `backend/alembic/versions/0001_create_users_farms_fields.py`
- **Depends on**: Task 1.2
- **Acceptance criteria**:
  - `alembic upgrade head` creates all three tables without error
  - `alembic downgrade -1` drops all three tables cleanly
  - Migration script includes `op.execute("CREATE EXTENSION IF NOT EXISTS postgis")` as a safety guard
  - `fields` table has a GIST spatial index on the `geometry` column
  - `fields` table has a GIN or B-tree index on `farm_id`
  - Running `alembic upgrade head` twice is idempotent (no errors on second run)
- **Tech**: Alembic, PostgreSQL 15, PostGIS
- **Assigned to**: Software-Developer

---

### Task 1.4: Farm & Field CRUD API Endpoints

- **What**: Implement the full CRUD API for farms and fields. All endpoints require authentication via `get_current_user`. Enforce per-plan field limits (Starter: 50, Farmer: 200, Pro/Enterprise: unlimited). Implement GeoJSON validation for field geometry input. All endpoints use Pydantic schemas for request/response serialization.
- **Files to create/modify**:
  - `backend/app/schemas/__init__.py`
  - `backend/app/schemas/farm.py`
  - `backend/app/schemas/field.py`
  - `backend/app/api/routes/farms.py`
  - `backend/app/api/routes/fields.py`
  - `backend/app/api/routes/__init__.py`
  - `backend/main.py`
- **Depends on**: Task 1.3
- **Acceptance criteria**:
  - `GET /api/v1/farms` returns list of farms for authenticated user
  - `POST /api/v1/farms` creates a farm for authenticated user
  - `GET /api/v1/farms/{farmId}` returns farm owned by authenticated user, 404 if not found or not owned
  - `PUT /api/v1/farms/{farmId}` updates farm name
  - `DELETE /api/v1/farms/{farmId}` deletes farm and all associated fields (cascade)
  - `GET /api/v1/fields` returns all fields across all farms for authenticated user
  - `POST /api/v1/fields` creates a field; validates GeoJSON polygon geometry; rejects if geometry is not a polygon; rejects if field count would exceed plan limit; computes and stores `area_ha`; accepts geometry as GeoJSON `{"type": "Polygon", "coordinates": [...]}`
  - `GET /api/v1/fields/{fieldId}` returns field with geometry as GeoJSON, 404 if not owned
  - `PUT /api/v1/fields/{fieldId}` updates field name, crop_type, planting_date, or geometry
  - `DELETE /api/v1/fields/{fieldId}` deletes field
  - All endpoints return appropriate HTTP status codes (201 on create, 204 on delete, 422 on validation error)
  - `GET /api/v1/fields` supports `?farm_id=<uuid>` query parameter to filter by farm
  - Integration tests in `backend/tests/test_fields_api.py` cover all endpoints including auth failure, ownership enforcement, plan limit enforcement
- **Tech**: FastAPI, SQLAlchemy 2.0, GeoAlchemy2, Pydantic v2, Shapely
- **Assigned to**: Software-Developer

---

### Task 1.5: Frontend — Login & Signup Pages

- **What**: Build the authentication pages using Supabase Auth client-side SDK. Implement email+password sign-up (with email verification), email+password login, Google OAuth login, and password reset flow. Implement a protected route wrapper that redirects unauthenticated users to `/login`. Store the Supabase session and expose a `useAuth` hook for use across the app.
- **Files to create/modify**:
  - `frontend/app/(auth)/login/page.tsx`
  - `frontend/app/(auth)/signup/page.tsx`
  - `frontend/app/(auth)/reset-password/page.tsx`
  - `frontend/app/(auth)/layout.tsx`
  - `frontend/lib/supabase/client.ts`
  - `frontend/lib/supabase/server.ts`
  - `frontend/lib/supabase/middleware.ts`
  - `frontend/middleware.ts`
  - `frontend/hooks/useAuth.ts`
  - `frontend/components/auth/AuthForm.tsx`
  - `frontend/components/auth/GoogleSignInButton.tsx`
- **Depends on**: Task 0.6
- **Acceptance criteria**:
  - Sign-up form collects: email, password (min 8 chars, 1 uppercase, 1 number), password confirmation
  - Sign-up triggers Supabase email verification; user sees "Check your email" message after submission
  - Login form logs in with email+password; on success redirects to `/dashboard`
  - "Continue with Google" button triggers Supabase OAuth flow and redirects to `/dashboard` on success
  - Password reset form sends reset email via Supabase; user sees confirmation message
  - `middleware.ts` runs on all `/dashboard/*` routes and redirects to `/login` if session is not present
  - `useAuth` hook provides: `user`, `session`, `loading`, `signOut()` function
  - All auth forms display field-level validation errors using `react-hook-form` + `zod`
  - Forms are fully keyboard-navigable and WCAG 2.1 AA compliant
- **Tech**: Next.js 14 App Router, Supabase Auth, @supabase/auth-helpers-nextjs, react-hook-form, zod
- **Assigned to**: Software-Developer

---

### Task 1.6: Frontend — Account Settings Page

- **What**: Build the account settings page at `/dashboard/settings` where users can update their profile (name, farm name, country, phone number) and request GDPR data deletion. Calls the backend `PUT /api/v1/users/me` endpoint. Implements the GDPR deletion request flow with a confirmation dialog.
- **Files to create/modify**:
  - `frontend/app/(dashboard)/settings/page.tsx`
  - `frontend/components/settings/ProfileForm.tsx`
  - `frontend/components/settings/DeleteAccountDialog.tsx`
  - `backend/app/api/routes/users.py`
  - `backend/app/schemas/user.py`
- **Depends on**: Task 1.5
- **Acceptance criteria**:
  - Settings page renders with pre-filled current user values fetched from `GET /api/v1/users/me`
  - Saving updates calls `PUT /api/v1/users/me`; displays success toast on save
  - "Delete my account" button opens a confirmation dialog with text: "Type DELETE to confirm account deletion"
  - Confirmed deletion calls `DELETE /api/v1/users/me`, which deletes the user record and triggers Supabase user deletion via Admin API; redirects to `/` on completion
  - `GET /api/v1/users/me` returns current user profile
  - `PUT /api/v1/users/me` updates profile fields; validates country is valid ISO 3166-1 alpha-2
  - `DELETE /api/v1/users/me` requires password re-authentication before deletion (Supabase re-auth flow)
- **Tech**: Next.js 14, FastAPI, Supabase Admin API, react-hook-form, zod
- **Assigned to**: Software-Developer

---

## Phase 2: Satellite Imagery Pipeline

**Goal:** Build the end-to-end pipeline that fetches Sentinel-2 imagery for user fields, computes NDVI and NDRE vegetation indices, stores results, and runs automatically on a schedule.

**Dependencies:** All Phase 1 tasks must be complete.

---

### Task 2.1: Sentinel Hub API Client & Authentication

- **What**: Implement the Sentinel Hub API client module using the `sentinelhub` Python SDK. Configure OAuth2 service account authentication using `SENTINEL_HUB_CLIENT_ID` and `SENTINEL_HUB_CLIENT_SECRET`. Implement a wrapper class `SentinelHubClient` that exposes methods for: (a) searching available scenes by bounding box and date range using the Catalog API, and (b) downloading specific bands via the Process API.
- **Files to create/modify**:
  - `ml/sentinel/client.py`
  - `ml/sentinel/__init__.py`
  - `ml/__init__.py`
  - `ml/requirements.txt`
- **Depends on**: Task 0.5
- **Acceptance criteria**:
  - `SentinelHubClient` can be instantiated with credentials from environment variables
  - `search_scenes(bbox: list[float], start_date: str, end_date: str, max_cloud_cover: float) -> list[Scene]` returns a list of available Sentinel-2 L2A scenes as typed dataclass instances with fields: `scene_id`, `date`, `cloud_cover_pct`, `tile_id`
  - `download_bands(scene_id: str, bbox: list[float], bands: list[str], resolution: int) -> dict[str, np.ndarray]` downloads specified bands and returns them as a dict of band name → numpy array
  - Authentication token is cached and auto-refreshed on expiry
  - Unit test `ml/tests/test_sentinel_client.py` mocks the Sentinel Hub API and verifies correct request construction for both search and download operations
  - Client raises `SentinelHubError` (custom exception) with descriptive message on API errors
  - `ml/requirements.txt` pins: `sentinelhub==3.10.*`, `numpy==1.26.*`, `rasterio==1.3.*`, `geopandas==0.14.*`, `shapely==2.0.*`, `scikit-learn==1.4.*`, `torch==2.2.*`, `pyproj==3.6.*`
- **Tech**: sentinelhub Python SDK 3.10, OAuth2, Python 3.11
- **Assigned to**: Software-Developer

---

### Task 2.2: Field Imagery Fetch Background Job

- **What**: Implement the Celery background task that, for each active field in the database, searches for available Sentinel-2 scenes in the last 30 days using the field's bounding box, selects scenes with cloud cover < 80%, downloads the required bands (B02, B03, B04, B05, B08, B11), and stores the raw band arrays as Cloud-Optimized GeoTIFF files in S3. Implement the database model `SatelliteScene` to track downloaded scenes per field.
- **Files to create/modify**:
  - `backend/app/models/satellite_scene.py`
  - `backend/app/worker/__init__.py`
  - `backend/app/worker/celery_app.py`
  - `backend/app/worker/tasks/imagery.py`
  - `backend/app/services/s3_storage.py`
- **Depends on**: Task 2.1, Task 1.4
- **Acceptance criteria**:
  - `SatelliteScene` model has columns: `id` (UUID, PK), `field_id` (UUID, FK → fields.id), `scene_id` (string, Sentinel Hub scene identifier), `acquired_at` (datetime), `cloud_cover_pct` (numeric(5,2)), `bands_s3_key` (string, S3 key prefix for stored bands), `status` (enum: pending/processing/complete/failed), `created_at`
  - Celery task `fetch_field_imagery(field_id: str)` downloads bands and stores them to S3 at key pattern `imagery/{field_id}/{scene_id}/`; creates a `SatelliteScene` record with status=complete on success
  - `s3_storage.py` implements `upload_geotiff(key: str, data: np.ndarray, profile: dict) -> str` and `download_geotiff(key: str) -> tuple[np.ndarray, dict]` using boto3
  - All S3 uploads set `ServerSideEncryption: AES256`
  - Task handles `SentinelHubError` gracefully: marks scene as failed, logs error, does not crash the worker
  - Integration test using mocked S3 (moto) and mocked Sentinel Hub client confirms task creates `SatelliteScene` record with correct metadata
- **Tech**: Celery 5.3, Redis, boto3, rasterio, sentinelhub SDK
- **Assigned to**: Software-Developer

---

### Task 2.3: Vegetation Index Computation (NDVI & NDRE)

- **What**: Implement the vegetation index computation module in `ml/`. Functions to compute per-pixel NDVI and NDRE from band arrays, apply cloud masking using the SCL band, and generate 10-day median composites by aggregating multiple scenes in a compositing window. Store computed index rasters as COG GeoTIFFs in S3. Create the `VegetationIndex` database model to track computed composites per field per time window.
- **Files to create/modify**:
  - `ml/indices/ndvi.py`
  - `ml/indices/ndre.py`
  - `ml/indices/composite.py`
  - `ml/indices/__init__.py`
  - `ml/cloud_mask.py`
  - `backend/app/models/vegetation_index.py`
  - `backend/app/worker/tasks/indices.py`
- **Depends on**: Task 2.2
- **Acceptance criteria**:
  - `compute_ndvi(nir: np.ndarray, red: np.ndarray, mask: np.ndarray) -> np.ndarray` computes `(nir - red) / (nir + red)`, applies mask (sets masked pixels to NaN), returns float32 array with values in [-1, 1]; no divide-by-zero errors (handled with `np.errstate`)
  - `compute_ndre(red_edge: np.ndarray, red: np.ndarray, mask: np.ndarray) -> np.ndarray` computes `(red_edge - red) / (red_edge + red)` with same masking behavior
  - `apply_scl_cloud_mask(scl: np.ndarray) -> np.ndarray` returns boolean mask where True=valid pixel, False=cloud/shadow/snow/water; SCL classes masked out: 0 (no data), 1 (saturated), 3 (cloud shadow), 8 (cloud medium confidence), 9 (cloud high confidence), 10 (thin cirrus), 11 (snow/ice)
  - `compute_composite(index_arrays: list[np.ndarray], method: str = "median") -> np.ndarray` computes pixel-wise median (or mean) across temporal stack, ignoring NaN; returns float32 array
  - `VegetationIndex` model has columns: `id` (UUID, PK), `field_id` (UUID, FK), `composite_start` (date), `composite_end` (date), `index_type` (enum: ndvi/ndre), `s3_key` (string), `mean_value` (numeric(6,4)), `min_value` (numeric(6,4)), `max_value` (numeric(6,4)), `valid_pixel_pct` (numeric(5,2)), `created_at`
  - Celery task `compute_field_indices(field_id: str, composite_start: str, composite_end: str)` orchestrates retrieval of scenes in window → cloud mask → NDVI/NDRE computation → composite → S3 upload → VegetationIndex record creation
  - Unit tests in `ml/tests/test_indices.py` verify correct NDVI/NDRE values with synthetic band data, correct masking behavior, and NaN handling
- **Tech**: numpy 1.26, rasterio 1.3, Python 3.11
- **Assigned to**: Software-Developer

---

### Task 2.4: Imagery Pipeline Scheduler (Cron Job)

- **What**: Implement the periodic Celery Beat scheduler that runs daily to find all active fields, checks if any fields have no composite more recent than 10 days, and enqueues `fetch_field_imagery` and `compute_field_indices` tasks for those fields. Implement a `PipelineRun` model to track daily scheduler executions for monitoring purposes.
- **Files to create/modify**:
  - `backend/app/worker/beat_schedule.py`
  - `backend/app/models/pipeline_run.py`
  - `backend/app/worker/tasks/scheduler.py`
- **Depends on**: Task 2.3
- **Acceptance criteria**:
  - Celery Beat schedule runs `trigger_daily_imagery_pipeline` task every day at 02:00 UTC
  - `trigger_daily_imagery_pipeline` queries all fields where the most recent `VegetationIndex.composite_end` is older than 10 days (or no composites exist), then enqueues one `fetch_field_imagery` chain per such field
  - `PipelineRun` model has columns: `id` (UUID, PK), `run_at` (datetime), `fields_processed` (int), `fields_failed` (int), `status` (enum: running/complete/failed), `error_message` (text, nullable)
  - `beat_schedule.py` uses `celery.schedules.crontab(hour=2, minute=0)` and is importable without side effects
  - Integration test verifies that fields with stale composites are correctly selected and tasks are enqueued
- **Tech**: Celery Beat 5.3, Redis, SQLAlchemy 2.0
- **Assigned to**: Software-Developer

---

### Task 2.5: Alembic Migration — Satellite Scenes, Vegetation Indices, Pipeline Runs

- **What**: Generate and finalize the Alembic migration that creates the `satellite_scenes`, `vegetation_indices`, and `pipeline_runs` tables introduced in Tasks 2.2–2.4.
- **Files to create/modify**:
  - `backend/alembic/versions/0002_create_imagery_pipeline_tables.py`
- **Depends on**: Task 2.4
- **Acceptance criteria**:
  - `alembic upgrade head` creates all three new tables without error
  - `alembic downgrade -1` drops the three tables cleanly
  - `satellite_scenes` has an index on `(field_id, acquired_at)` for efficient time-range queries
  - `vegetation_indices` has an index on `(field_id, composite_end DESC)` for efficient "latest composite" queries
  - `vegetation_indices` has a unique constraint on `(field_id, composite_start, composite_end, index_type)` to prevent duplicate computations
- **Tech**: Alembic, PostgreSQL 15
- **Assigned to**: Software-Developer

---

## Phase 3: AI Pesticide Prescription Engine

**Goal:** Build the management zone delineation algorithm, the rule-based VRA prescription engine, and the export pipeline (GeoJSON + ISOBUS shapefile + PDF report). Expose the prescription API endpoints.

**Dependencies:** All Phase 2 tasks must be complete.

---

### Task 3.1: Management Zone Delineation (k-means Clustering)

- **What**: Implement the management zone delineation algorithm in `ml/zones/`. Uses k-means clustering (k=3) on the combined NDVI and NDRE composite raster values per field to produce three zone polygons labeled Low, Medium, and High. Applies minimum zone size filter (merge zones smaller than 0.5 ha into dominant adjacent zone). Outputs zone polygons as GeoDataFrame in EPSG:4326.
- **Files to create/modify**:
  - `ml/zones/__init__.py`
  - `ml/zones/delineation.py`
  - `ml/zones/zone_filter.py`
  - `backend/app/models/management_zone.py`
  - `backend/app/worker/tasks/zones.py`
- **Depends on**: Task 2.3
- **Acceptance criteria**:
  - `delineate_zones(ndvi: np.ndarray, ndre: np.ndarray, field_geometry: dict, transform: Affine) -> gpd.GeoDataFrame` runs k-means (k=3) on the combined [NDVI, NDRE] feature matrix; assigns zone labels based on cluster centroid ordering (Low=lowest NDVI cluster, High=highest NDVI cluster); vectorizes raster zones to polygons; reprojects to EPSG:4326; returns GeoDataFrame with columns `zone_label` (str: Low/Medium/High) and `geometry`
  - `filter_minimum_zone_size(gdf: gpd.GeoDataFrame, min_ha: float = 0.5) -> gpd.GeoDataFrame` merges zones smaller than `min_ha` into the spatially adjacent dominant zone
  - Zone delineation completes in under 60 seconds for a 500 ha field on a single CPU core
  - `ManagementZone` model has columns: `id` (UUID, PK), `field_id` (UUID, FK), `vegetation_index_id` (UUID, FK → vegetation_indices.id), `zone_label` (enum: Low/Medium/High), `geometry` (Geometry(Polygon, srid=4326)), `area_ha` (numeric(10,2)), `mean_ndvi` (numeric(6,4)), `created_at`
  - Unit tests in `ml/tests/test_delineation.py` verify: correct zone label ordering, minimum size filtering, polygon validity (no self-intersections), correct output CRS
- **Tech**: scikit-learn 1.4 (KMeans), geopandas 0.14, shapely 2.0, rasterio 1.3, pyproj 3.6
- **Assigned to**: Software-Developer

---

### Task 3.2: VRA Prescription Engine & API Endpoint

- **What**: Implement the prescription engine that translates management zone labels into application rate multipliers based on crop type and application type. Implement the `POST /api/v1/fields/{fieldId}/prescriptions` endpoint that triggers zone delineation (if not already done for the latest composite), applies the prescription rules, stores the result, and returns the prescription GeoJSON. Implement the `GET /api/v1/fields/{fieldId}/prescriptions` endpoint to list available prescriptions.
- **Files to create/modify**:
  - `ml/prescription/engine.py`
  - `ml/prescription/__init__.py`
  - `backend/app/models/prescription.py`
  - `backend/app/schemas/prescription.py`
  - `backend/app/api/routes/prescriptions.py`
  - `backend/app/services/prescription_service.py`
- **Depends on**: Task 3.1
- **Acceptance criteria**:
  - Prescription engine applies multipliers per the CEO spec exactly:
    - Fungicide: Low=0.6x, Medium=1.0x, High=1.3x
    - Herbicide: Low=0.7x, Medium=1.0x, High=1.2x
    - Insecticide: Low=0.5x, Medium=1.0x, High=1.5x
  - `POST /api/v1/fields/{fieldId}/prescriptions` body: `{"base_rate_l_ha": float, "application_type": "fungicide"|"herbicide"|"insecticide"}` → returns prescription GeoJSON FeatureCollection with `zone_label`, `rate_l_ha`, `rate_pct` attributes per feature
  - `GET /api/v1/fields/{fieldId}/prescriptions` returns list of prescriptions with: `id`, `created_at`, `application_type`, `base_rate_l_ha`, `composite_date_range`, `estimated_savings_pct`
  - `GET /api/v1/fields/{fieldId}/prescriptions/{prescriptionId}` returns full prescription GeoJSON
  - `Prescription` model has columns: `id` (UUID, PK), `field_id` (UUID, FK), `management_zone_set_id` (UUID, FK → management zone computation), `application_type` (enum), `base_rate_l_ha` (numeric(8,3)), `estimated_savings_pct` (numeric(5,2), computed as weighted average saving vs. uniform 1.0x rate), `geojson_s3_key` (string), `created_at`
  - `estimated_savings_pct` computed as: `sum_zones((1.0 - multiplier) * zone_area_ha) / total_field_area_ha * 100`; positive value = savings
  - All endpoints require authentication and field ownership verification
  - Unit tests in `backend/tests/test_prescription_engine.py` verify all three application type multiplier sets and `estimated_savings_pct` calculation
- **Tech**: FastAPI, SQLAlchemy 2.0, scikit-learn, geopandas, Pydantic v2
- **Assigned to**: Software-Developer

---

### Task 3.3: Shapefile & PDF Export

- **What**: Implement the export pipeline that generates ISOBUS-compatible ESRI Shapefiles and PDF prescription reports from a prescription record. Implement the `GET /api/v1/fields/{fieldId}/prescriptions/{id}/export` endpoint that returns a presigned S3 URL for the requested format.
- **Files to create/modify**:
  - `backend/app/services/export/shapefile.py`
  - `backend/app/services/export/pdf_report.py`
  - `backend/app/services/export/__init__.py`
  - `backend/app/api/routes/exports.py`
- **Depends on**: Task 3.2
- **Acceptance criteria**:
  - Shapefile export produces a ZIP archive containing: `prescription.shp`, `prescription.dbf`, `prescription.prj`, `prescription.shx` in WGS84 (EPSG:4326)
  - Shapefile attribute table contains exactly: `ZoneID` (string), `RateL_ha` (float, application rate in L/ha), `RatePct` (float, percentage of base rate, e.g. 60.0 for 0.6x), `ZoneLabel` (string: Low/Medium/High)
  - PDF report includes: AgroLens logo placeholder, farm name, field name, generation date, crop type, application type, base rate (L/ha), zone map image (PNG render of zones on white background), zone area breakdown table (zone label / area ha / rate L/ha / rate pct), estimated input savings (%), disclaimer text: "This prescription is a decision support tool. Review with a qualified agronomist before application."
  - `GET /api/v1/fields/{fieldId}/prescriptions/{id}/export?format=shp` returns `{"download_url": "<presigned S3 URL>", "expires_in": 3600}`
  - `GET /api/v1/fields/{fieldId}/prescriptions/{id}/export?format=pdf` returns same structure for PDF
  - `GET /api/v1/fields/{fieldId}/prescriptions/{id}/export?format=geojson` returns the GeoJSON directly (not via S3 presigned URL, inline in response)
  - Presigned URLs expire in 1 hour
  - Export files are stored in S3 at key pattern: `exports/{field_id}/{prescription_id}/prescription.{ext}`
  - Unit tests verify shapefile attribute schema and that PDF contains required text sections
- **Tech**: geopandas 0.14, fiona, reportlab (or weasyprint), matplotlib (for zone map render), boto3
- **Assigned to**: Software-Developer

---

### Task 3.4: Alembic Migration — Management Zones & Prescriptions

- **What**: Generate and finalize the Alembic migration that creates the `management_zones` and `prescriptions` tables introduced in Tasks 3.1–3.2.
- **Files to create/modify**:
  - `backend/alembic/versions/0003_create_zones_prescriptions.py`
- **Depends on**: Task 3.3
- **Acceptance criteria**:
  - `alembic upgrade head` creates both new tables without error
  - `alembic downgrade -1` drops both tables cleanly
  - `management_zones` table has a GIST spatial index on `geometry`
  - `management_zones` table has an index on `(field_id, created_at DESC)` for fetching the latest zone set per field
  - `prescriptions` table has an index on `(field_id, created_at DESC)`
- **Tech**: Alembic, PostgreSQL 15, PostGIS
- **Assigned to**: Software-Developer

---

### Task 3.5: NDVI Time-Series API Endpoint

- **What**: Implement the `GET /api/v1/fields/{fieldId}/ndvi-timeseries` endpoint that returns the 12-month rolling history of NDVI mean values per field as a time-series array. This satisfies REQ-13 and feeds the dashboard chart in Phase 4.
- **Files to create/modify**:
  - `backend/app/api/routes/analytics.py`
  - `backend/app/schemas/analytics.py`
- **Depends on**: Task 2.5
- **Acceptance criteria**:
  - `GET /api/v1/fields/{fieldId}/ndvi-timeseries` returns `{"field_id": "<id>", "data": [{"date": "YYYY-MM-DD", "ndvi_mean": float, "ndvi_min": float, "ndvi_max": float}], "unit": "ndvi", "period_days": 365}`
  - Data is sorted ascending by date
  - Each entry's date is the `composite_end` date of the corresponding `VegetationIndex` record
  - Only NDVI index type records are returned (not NDRE)
  - Returns empty `data: []` array (not 404) if no composites exist yet for the field
  - Requires authentication and field ownership
  - Response time under 200ms for 365 days of data (appropriate database index exists)
- **Tech**: FastAPI, SQLAlchemy 2.0, Pydantic v2
- **Assigned to**: Software-Developer

---

## Phase 4: Farmer Dashboard

**Goal:** Build the full farmer-facing web dashboard: field map overview, NDVI heatmap overlay, prescription zone overlay, time-series charts, export buttons, notifications, mobile-responsiveness, and the remaining REQ-13 API endpoints.

**Dependencies:** All Phase 3 tasks must be complete.

---

### Task 4.1: Field Boundary Upload & Map Drawing UI

- **What**: Build the field management UI where farmers can: (a) upload a GeoJSON or KML file to create a field, and (b) draw a polygon directly on a Mapbox GL JS map. The UI calls the `POST /api/v1/fields` endpoint. Include a field list sidebar showing all fields with their names, crop types, and area.
- **Files to create/modify**:
  - `frontend/app/(dashboard)/fields/page.tsx`
  - `frontend/app/(dashboard)/fields/new/page.tsx`
  - `frontend/components/fields/FieldList.tsx`
  - `frontend/components/fields/FieldUploadForm.tsx`
  - `frontend/components/fields/FieldDrawMap.tsx`
  - `frontend/lib/api/fields.ts`
  - `frontend/lib/mapbox/drawing.ts`
- **Depends on**: Task 1.5
- **Acceptance criteria**:
  - Upload form accepts `.geojson` and `.kml` file types; parses the file client-side and extracts the first polygon feature; rejects files with no polygon geometry with an error message
  - KML upload: converts KML polygon to GeoJSON client-side before sending to API (using `@mapbox/togeojson` or equivalent)
  - Map drawing uses Mapbox GL Draw (`@mapbox/mapbox-gl-draw`) to draw a free-form polygon; "Finish Drawing" button submits the polygon geometry
  - Field creation form collects: field name, crop type (dropdown), planting date (date picker); all fields validated before submission
  - On successful creation, redirects to the field detail page
  - Field list shows all fields with: name, crop type icon, area (ha), health status badge (Green/Amber/Red based on NDVI deviation — placeholder "Calculating..." if no composites yet)
  - Field list supports sorting by: name (alphabetical), area (descending), health status
  - Mobile-responsive: file upload and field list work on 10-inch tablet in landscape
- **Tech**: Next.js 14, Mapbox GL JS 3, @mapbox/mapbox-gl-draw, @mapbox/togeojson, react-hook-form, zod
- **Assigned to**: Software-Developer

---

### Task 4.2: Dashboard Home — Field Overview Map

- **What**: Build the main dashboard landing page at `/dashboard` showing a Mapbox GL JS map with all user fields rendered as colored polygons (Green/Amber/Red health status), and a summary panel showing total fields, total hectares, fields with alerts, and plan usage (current ha vs. plan limit).
- **Files to create/modify**:
  - `frontend/app/(dashboard)/page.tsx`
  - `frontend/app/(dashboard)/layout.tsx`
  - `frontend/components/dashboard/FieldOverviewMap.tsx`
  - `frontend/components/dashboard/SummaryPanel.tsx`
  - `frontend/components/dashboard/PlanUsageBar.tsx`
  - `frontend/components/layout/Sidebar.tsx`
  - `frontend/components/layout/TopNav.tsx`
- **Depends on**: Task 4.1
- **Acceptance criteria**:
  - Map renders all user fields as GeoJSON polygons; colors: `#22c55e` (Green = normal), `#f59e0b` (Amber = mild stress, NDVI 10–15% below 30-day avg), `#ef4444` (Red = significant stress, NDVI >15% below 30-day avg)
  - Clicking a field polygon navigates to `/dashboard/fields/{fieldId}`
  - Map auto-fits viewport to show all fields on load using `fitBounds`
  - Summary panel shows: "X fields", "X.X ha total", "X fields with alerts", "X / Y ha used (plan limit)"
  - `PlanUsageBar` shows a progress bar; turns amber at 80% of plan limit; turns red at 95%; shows "Upgrade" CTA button
  - Sidebar navigation links: Dashboard, Fields, Settings, Billing; active route highlighted
  - `TopNav` shows: AgroLens logo, user's farm name, sign-out button
  - Dashboard layout uses CSS Grid with a fixed sidebar (240px) and scrollable main content area
  - Page fully functional on a 10-inch tablet in landscape orientation
- **Tech**: Next.js 14, Mapbox GL JS 3, Tailwind CSS
- **Assigned to**: Software-Developer

---

### Task 4.3: Field Detail View — NDVI Chart & Prescription Map

- **What**: Build the field detail page at `/dashboard/fields/{fieldId}` showing: the NDVI time-series line chart (12 months), the current prescription zone map overlaid on Mapbox satellite basemap, the zone breakdown table, and the export buttons.
- **Files to create/modify**:
  - `frontend/app/(dashboard)/fields/[fieldId]/page.tsx`
  - `frontend/components/fields/NdviChart.tsx`
  - `frontend/components/fields/PrescriptionZoneMap.tsx`
  - `frontend/components/fields/ZoneBreakdownTable.tsx`
  - `frontend/components/fields/ExportButtons.tsx`
  - `frontend/lib/api/prescriptions.ts`
  - `frontend/lib/api/analytics.ts`
- **Depends on**: Task 4.2, Task 3.5
- **Acceptance criteria**:
  - NDVI chart uses Recharts `LineChart`; x-axis: dates; y-axis: NDVI 0–1; shows a shaded reference band for ±1 standard deviation of the 30-day rolling average; tooltip on hover shows date + NDVI value
  - If no NDVI data exists yet, displays a placeholder: "Satellite analysis in progress. Check back in 24 hours."
  - Prescription zone map renders the latest prescription GeoJSON as a fill layer on Mapbox satellite basemap; zone colors: `#22c55e` (Low), `#f59e0b` (Medium), `#ef4444` (High); legend displayed in bottom-left corner
  - Imagery date displayed below map: "Based on imagery: [composite_start] — [composite_end]"
  - Alert banner shown if most recent composite is older than 21 days: "Cloud cover is preventing fresh imagery. Showing data from [date]. Consider applying uniform rate."
  - Zone breakdown table columns: Zone (Low/Medium/High), Area (ha), Recommended Rate (L/ha), % of Base Rate
  - "Generate Prescription" button opens a modal form: inputs = application type (dropdown) + base rate (numeric input); submits `POST /api/v1/fields/{fieldId}/prescriptions`; on success refreshes the prescription map
  - Export button group: "Download Shapefile" and "Download PDF" each call the export endpoint and trigger browser download via the presigned S3 URL; "Copy GeoJSON" copies the GeoJSON to clipboard
- **Tech**: Next.js 14, Recharts 2, Mapbox GL JS 3, Tailwind CSS
- **Assigned to**: Software-Developer

---

### Task 4.4: Mobile-Responsive Design & Offline Map Caching

- **What**: Audit and fix all dashboard pages for full usability on a 10-inch tablet (landscape) at 1280×800. Implement a Next.js service worker (via `next-pwa` or a custom service worker) that caches the prescription zone GeoJSON and Mapbox tiles for the currently selected field, enabling offline viewing with a "Last updated: [date]" indicator.
- **Files to create/modify**:
  - `frontend/public/sw.js`
  - `frontend/lib/service-worker/cache-strategies.ts`
  - `frontend/next.config.js`
  - `frontend/app/layout.tsx`
- **Depends on**: Task 4.3
- **Acceptance criteria**:
  - All dashboard pages pass a Lighthouse mobile audit with a score of 85+ on Performance and 90+ on Accessibility
  - Sidebar collapses to a bottom navigation bar on screens narrower than 768px
  - VRA zone map renders correctly at 1280×800 landscape (tablet breakpoint)
  - Service worker intercepts and caches: (a) `GET /api/v1/fields/{fieldId}/prescriptions/{id}` response, (b) Mapbox tile requests for the currently viewed field extent
  - When offline, the map renders the cached prescription zones with a yellow banner: "Offline mode — Last updated: [ISO date]"
  - Service worker uses a cache-first strategy for map tiles and a network-first (with cache fallback) strategy for API responses
  - PWA manifest configured: `name: "AgroLens"`, `short_name: "AgroLens"`, `theme_color: "#16a34a"`, `background_color: "#ffffff"`, `display: "standalone"`
- **Tech**: Next.js 14, next-pwa or Workbox, Service Workers API
- **Assigned to**: Software-Developer

---

### Task 4.5: Email Notifications System

- **What**: Implement the notification system that sends email alerts to farmers when: (a) a new VRA map is ready for any of their fields, and (b) field NDVI drops more than 15% below the 30-day rolling average. Implement user-configurable notification preferences per field. Use SendGrid for email delivery.
- **Files to create/modify**:
  - `backend/app/services/notifications.py`
  - `backend/app/models/notification_preference.py`
  - `backend/app/worker/tasks/notifications.py`
  - `backend/app/api/routes/notification_preferences.py`
  - `backend/app/schemas/notification_preference.py`
  - `backend/templates/email/new_vra_map.html`
  - `backend/templates/email/field_stress_alert.html`
- **Depends on**: Task 4.3, Task 2.5
- **Acceptance criteria**:
  - `NotificationPreference` model has columns: `id` (UUID, PK), `user_id` (UUID, FK), `field_id` (UUID, FK, nullable — null means applies to all user fields), `notification_type` (enum: new_vra_map/field_stress_alert), `enabled` (bool, default true), `updated_at`
  - `send_email(to: str, subject: str, html_body: str)` uses SendGrid Python SDK; logs send success/failure; retries once on transient SendGrid error
  - Celery task `send_new_vra_map_notification(prescription_id: str)` is triggered after a prescription is successfully created; checks `NotificationPreference` for the field; sends email if enabled
  - Celery task `check_stress_alerts()` runs daily after `compute_field_indices`; for each field with a new composite, computes deviation from 30-day rolling average; enqueues `send_stress_alert_email(field_id, ndvi_deviation_pct)` if deviation > 15%
  - Email templates are HTML with inline CSS; include AgroLens branding, field name, map thumbnail (placeholder image link for MVP), CTA button "View Field"
  - `GET /api/v1/notification-preferences` returns all preferences for current user
  - `PUT /api/v1/notification-preferences/{id}` toggles enabled/disabled
  - Integration test verifies that creating a prescription enqueues the notification task with correct arguments
- **Tech**: SendGrid Python SDK, Celery, SQLAlchemy, Jinja2 (for email templates)
- **Assigned to**: Software-Developer

---

### Task 4.6: Complete REST API (REQ-13 Remaining Endpoints)

- **What**: Implement the remaining REQ-13 API endpoints not yet covered by Tasks 1.4, 3.2, and 3.5. Add API key authentication (Bearer token generated in account settings). Implement rate limiting (100 req/min per API key). Publish the OpenAPI specification. Add hectare usage metering endpoint.
- **Files to create/modify**:
  - `backend/app/models/api_key.py`
  - `backend/app/schemas/api_key.py`
  - `backend/app/api/routes/api_keys.py`
  - `backend/app/core/rate_limiting.py`
  - `backend/app/api/deps.py`
  - `backend/main.py`
- **Depends on**: Task 4.5
- **Acceptance criteria**:
  - `ApiKey` model has columns: `id` (UUID, PK), `user_id` (UUID, FK), `name` (string, user-defined label), `key_hash` (string, bcrypt hash of the key), `key_prefix` (string(8), first 8 chars for display), `created_at`, `last_used_at` (datetime, nullable), `revoked` (bool, default false)
  - `POST /api/v1/api-keys` creates a new API key; returns the full key only once on creation (not stored in plain text); response: `{"key": "agro_sk_...", "id": "<uuid>", "name": "<name>", "prefix": "agro_sk_"}`
  - `GET /api/v1/api-keys` lists all non-revoked keys (prefix + name only, never full key)
  - `DELETE /api/v1/api-keys/{id}` marks key as revoked
  - All REQ-13 endpoints support both Supabase JWT auth and API key Bearer token auth
  - Rate limiting middleware: 100 requests/minute per API key using Redis sliding window counter; returns HTTP 429 with `Retry-After` header on limit exceeded
  - `GET /api/v1/account/usage` returns `{"hectares_used": float, "plan_limit": int | null, "usage_pct": float}` for the current billing period
  - OpenAPI spec accessible at `/v1/openapi.json`; includes all endpoints, request/response schemas, authentication schemes
  - `GET /api/v1/fields/{id}/vra-maps` is aliased to `GET /api/v1/fields/{id}/prescriptions` (backward compatibility alias)
  - `GET /api/v1/fields/{id}/vra-maps/{mapId}/export` is aliased to `GET /api/v1/fields/{id}/prescriptions/{mapId}/export`
- **Tech**: FastAPI, Redis (rate limiting), SQLAlchemy 2.0, passlib (bcrypt)
- **Assigned to**: Software-Developer

---

## Phase 5: Billing, Subscription & Monitoring

**Goal:** Integrate Stripe for subscription management with the three plan tiers, implement webhook handling, add usage metering and account restrictions, and set up production monitoring and alerting.

**Dependencies:** All Phase 4 tasks must be complete.

---

### Task 5.1: Stripe Subscription Integration

- **What**: Implement the Stripe billing integration. Build the checkout flow (redirect to Stripe Checkout), the billing portal (Stripe Customer Portal for self-service management), and the `Subscription` database model to track plan state. Implement the plan-based field limit enforcement (already referenced in Task 1.4, but the Stripe-driven plan state lives here).
- **Files to create/modify**:
  - `backend/app/models/subscription.py`
  - `backend/app/schemas/subscription.py`
  - `backend/app/services/stripe_service.py`
  - `backend/app/api/routes/billing.py`
  - `frontend/app/(dashboard)/billing/page.tsx`
  - `frontend/components/billing/PlanSelector.tsx`
  - `frontend/components/billing/CurrentPlanCard.tsx`
- **Depends on**: Task 4.6
- **Acceptance criteria**:
  - `Subscription` model has columns: `id` (UUID, PK), `user_id` (UUID, FK, unique), `stripe_customer_id` (string), `stripe_subscription_id` (string, nullable), `plan` (enum: free/starter/farmer/pro/enterprise), `status` (enum: active/past_due/cancelled/trialing), `current_period_start` (datetime), `current_period_end` (datetime), `hectare_limit` (int, nullable — null = unlimited), `cancelled_at` (datetime, nullable)
  - `POST /api/v1/billing/create-checkout-session` body: `{"price_id": "<Stripe Price ID>", "success_url": str, "cancel_url": str}` → creates a Stripe Checkout Session and returns `{"checkout_url": str}`; creates or retrieves Stripe Customer linked to user
  - `POST /api/v1/billing/create-portal-session` → creates Stripe Customer Portal session and returns `{"portal_url": str}`; requires active subscription
  - `GET /api/v1/billing/subscription` returns current subscription status
  - Billing page renders: current plan name, billing period, next payment date, hectare usage, upgrade/downgrade options with pricing table
  - Pricing table shows three plans: Starter (€49/mo, 100 ha), Farmer (€199/mo, 500 ha), Pro (€599/mo, 2,000 ha); annual pricing shown as "€X/yr (save 20%)"; "Current Plan" badge on active plan; "Upgrade" or "Downgrade" buttons on others
  - Billing page requires authentication; unauthenticated access redirects to `/login`
  - Free tier (no subscription): limited to 2 fields and 50 ha total; "Upgrade" CTA prominent on dashboard
- **Tech**: Stripe Python SDK 8.9, stripe.js, FastAPI, Next.js 14
- **Assigned to**: Software-Developer

---

### Task 5.2: Stripe Webhook Handler & Subscription Lifecycle

- **What**: Implement the Stripe webhook endpoint that handles all subscription lifecycle events. Implement the 7-day grace period for failed payments and automatic account restriction after grace period expiry.
- **Files to create/modify**:
  - `backend/app/api/routes/webhooks.py`
  - `backend/app/services/subscription_lifecycle.py`
  - `backend/app/worker/tasks/billing.py`
- **Depends on**: Task 5.1
- **Acceptance criteria**:
  - `POST /api/v1/webhooks/stripe` endpoint verifies Stripe webhook signature using `STRIPE_WEBHOOK_SECRET`; returns HTTP 400 on signature verification failure; returns HTTP 200 immediately after signature verification (before processing) to prevent Stripe timeouts; delegates processing to Celery task
  - Handles the following Stripe events:
    - `customer.subscription.created` → set `subscription.status = active`, set plan and hectare limit
    - `customer.subscription.updated` → update plan, status, period dates, hectare limit
    - `customer.subscription.deleted` → set `subscription.status = cancelled`, set `cancelled_at`
    - `invoice.payment_succeeded` → update `current_period_start` and `current_period_end`; clear any `past_due` flags
    - `invoice.payment_failed` → set `subscription.status = past_due`; log event; do NOT immediately restrict access
  - Grace period task: `check_past_due_subscriptions()` runs daily; finds subscriptions with `status = past_due` and `current_period_end < now() - 7 days`; restricts account (sets `hectare_limit = 0`); sends account restriction email via SendGrid
  - Unit tests cover: signature verification failure returns 400, valid `invoice.payment_failed` sets status to past_due, grace period expiry triggers restriction
- **Tech**: Stripe Python SDK, Celery, FastAPI, SQLAlchemy 2.0
- **Assigned to**: Software-Developer

---

### Task 5.3: Alembic Migration — Subscriptions & API Keys

- **What**: Generate and finalize the Alembic migration that creates the `subscriptions` and `api_keys` tables.
- **Files to create/modify**:
  - `backend/alembic/versions/0004_create_subscriptions_api_keys.py`
- **Depends on**: Task 5.2
- **Acceptance criteria**:
  - `alembic upgrade head` creates both tables without error
  - `alembic downgrade -1` drops both tables cleanly
  - `subscriptions` has a unique index on `user_id`
  - `subscriptions` has an index on `stripe_subscription_id`
  - `api_keys` has an index on `(user_id, revoked)` for listing active keys
  - `api_keys` has an index on `key_prefix` for key lookup during auth
- **Tech**: Alembic, PostgreSQL 15
- **Assigned to**: Software-Developer

---

### Task 5.4: Application Monitoring & Alerting Setup

- **What**: Integrate Sentry for frontend and backend error tracking. Configure Datadog APM (or equivalent) for API latency monitoring. Implement a custom pipeline monitoring endpoint that Datadog can poll to alert on stale field composites. Add structured logging throughout the backend.
- **Files to create/modify**:
  - `backend/app/core/logging.py`
  - `backend/app/core/monitoring.py`
  - `backend/app/api/routes/monitoring.py`
  - `backend/main.py`
  - `frontend/lib/sentry.ts`
  - `frontend/app/global-error.tsx`
  - `infra/datadog/datadog.yaml`
- **Depends on**: Task 5.2
- **Acceptance criteria**:
  - Sentry SDK initialized in both FastAPI (`sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)`) and Next.js (`Sentry.init(...)`) on application startup when `ENVIRONMENT` is not `development`
  - Unhandled exceptions in both frontend and backend are captured and appear in Sentry
  - Structured JSON logging via Python `logging` module: every log entry includes `timestamp`, `level`, `service`, `request_id`, `user_id` (if available), `message`
  - `GET /monitoring/pipeline-health` (internal endpoint, requires `X-Monitor-Key` header matching a shared secret) returns: `{"fields_total": int, "fields_stale": int, "fields_stale_ids": list[str], "last_pipeline_run": str}`; "stale" = no composite in last 21 days
  - `infra/datadog/datadog.yaml` configures Datadog Agent to scrape the `/monitoring/pipeline-health` endpoint every 5 minutes and alert when `fields_stale > 0`
  - Datadog (or equivalent) configured with alert: p95 API response time > 2000ms on any endpoint triggers PagerDuty/email alert
  - `GET /monitoring/pipeline-health` returns `fields_stale` count in under 500ms regardless of total field count (requires efficient query with index on `(field_id, composite_end DESC)`)
- **Tech**: Sentry SDK, Datadog Agent, Python logging, FastAPI
- **Assigned to**: Software-Developer

---

## Summary Table

| Phase | Tasks | Key Deliverable | REQs Addressed |
|---|---|---|---|
| 0 | 0.1–0.6 | Running monorepo with Docker, FastAPI skeleton, Next.js skeleton | REQ-14 (partial) |
| 1 | 1.1–1.6 | Auth, Farm/Field models, CRUD API, Login/Signup UI | REQ-01, REQ-11, REQ-15 (partial) |
| 2 | 2.1–2.5 | Sentinel-2 fetch, NDVI/NDRE computation, scheduled pipeline | REQ-02, REQ-03 |
| 3 | 3.1–3.5 | Zone delineation, prescription engine, shapefile/PDF export, analytics API | REQ-04, REQ-05, REQ-06, REQ-13 (partial) |
| 4 | 4.1–4.6 | Full farmer dashboard, mobile-responsive, notifications, complete API | REQ-07, REQ-08, REQ-09, REQ-10, REQ-13 |
| 5 | 5.1–5.4 | Stripe billing, subscription lifecycle, Sentry, monitoring | REQ-12, REQ-15, REQ-16 |

**Total tasks: 28**

---

## Dependency Graph

```
0.1 → 0.2
0.1 → 0.3 → 0.4 → 0.5
0.3 → 0.6
0.5 → 1.1 → 1.2 → 1.3 → 1.4
0.6 → 1.5 → 1.6
2.1 → [independent of Phase 1 models, but requires 0.5]
1.4 + 2.1 → 2.2 → 2.3 → 2.4 → 2.5
2.3 → 3.1 → 3.2 → 3.3 → 3.4
2.5 → 3.5
1.5 → 4.1 → 4.2 → 4.3
4.3 + 3.5 → 4.4 → 4.5 → 4.6
4.6 → 5.1 → 5.2 → 5.3
5.2 → 5.4
```
