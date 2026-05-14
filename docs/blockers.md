# AgroLens — Blockers & Open Questions

**Last updated:** 2026-05-12
**Author:** Software Developer Agent

---

## Phase 0 — No Hard Blockers

Phase 0 is fully implemented. The following items require action before the
system can be run end-to-end, but none block code completion:

---

## External Credentials Required Before Running

The following real credentials must be obtained and placed in `.env` files
before `docker-compose up` will function fully:

| Credential | Where to obtain | Affects |
|---|---|---|
| `SUPABASE_URL` + `SUPABASE_ANON_KEY` + `SUPABASE_JWT_SECRET` + `SUPABASE_SERVICE_ROLE_KEY` | Create a free project at supabase.com | Auth, JWT verification, user provisioning |
| `SENTINEL_HUB_CLIENT_ID` + `SENTINEL_HUB_CLIENT_SECRET` | apps.sentinel-hub.com (free tier available) | Satellite imagery pipeline (Phase 2) |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` + `AWS_S3_BUCKET_NAME` | AWS Console — create IAM user + S3 bucket in eu-central-1 | Imagery storage, export downloads (Phase 2+) |
| `STRIPE_SECRET_KEY` + `STRIPE_WEBHOOK_SECRET` + Price IDs | dashboard.stripe.com (test mode) | Billing (Phase 5) |
| `SENDGRID_API_KEY` + `SENDGRID_FROM_EMAIL` | app.sendgrid.com | Email notifications (Phase 4) |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | account.mapbox.com | Map rendering (Phase 4) |

For Phase 0 local testing, only the Supabase and PostgreSQL credentials are
strictly required. The others can remain as placeholder values — the backend
will start and the health endpoints will respond without them.

---

## Potential Issues to Monitor

### 1. GDAL version alignment in Docker

The `backend/Dockerfile` installs `libgdal32` (Debian bookworm package).
If `rasterio==1.3.*` or `geopandas==0.14.*` require a different GDAL ABI
version, the pip install step will fail.

**Resolution path:** Pin GDAL to the exact version available in the base image,
or use `osgeo/gdal:ubuntu-full-3.6.4` as the builder base image.

### 2. `torch==2.2.*` binary size

PyTorch adds ~2 GB to the Docker image. In Phase 0 it is not actively used.
Consider using `torch==2.2.* --index-url https://download.pytorch.org/whl/cpu`
to install the CPU-only variant (~700 MB), or deferring it to a separate
`ml` service Dockerfile.

**Resolution path:** Move `torch` and `scikit-learn` to `ml/requirements.txt`
and exclude from `backend/requirements.txt` until Phase 3 (ML pipeline
integration).

### 3. Next.js `serverActions.allowedOrigins` in production

`next.config.js` currently lists only `localhost:3000` in
`serverActions.allowedOrigins`. This must be updated to include the production
domain (e.g. `app.agrolens.io`) before staging/production deployment.

### 4. Supabase JWT Algorithm

The `security.py` implementation uses HS256 with `SUPABASE_JWT_SECRET`.
Supabase projects created after early 2024 support RS256 (asymmetric) in
addition to HS256. If the Supabase project is configured for RS256, the
backend must be updated to fetch the JWKS endpoint and verify with the
public key. Confirm the algorithm in Supabase Dashboard → Settings → API →
JWT Settings before Phase 1 testing.

---

## Phase 1+ Pre-requisites

The following must be completed before Phase 1 work begins:

1. Run `alembic upgrade head` against the running Postgres container to verify
   the baseline migration works.
2. Confirm `GET /health/db` returns `{"status": "ok"}` with PostGIS version.
3. Set up Supabase project and copy real credentials into `backend/.env`.
4. Create a Supabase OAuth app for Google sign-in (required for Task 1.5).

---

## Phase 1 — No Hard Blockers

Phase 1 (Tasks 1.1–1.6) is fully implemented. The following notes apply:

### 1. `alembic upgrade head` must be run

After Phase 1 code is deployed, run:

```
cd src/backend
alembic upgrade head
```

This applies migration `0001_create_users_farms_fields` which creates the
`users`, `farms`, and `fields` tables and the PostGIS geometry column.
The migration is idempotent — running it twice is safe.

### 2. GeoAlchemy2 `ST_GeomFromGeoJSON` in SQLAlchemy `select()`

The `fields.py` route uses `ST_GeomFromGeoJSON` directly in the ORM
`mapped_column` assignment for new geometry. If GeoAlchemy2 version
`0.15.*` does not support direct function assignment in this way, an
alternative is to use `func.ST_GeomFromGeoJSON(geojson_str)` from
`sqlalchemy.func` and cast with `WKBElement`. Verify against the running
container.

### 3. `get_current_user` function unwrapping in tests

The test file `test_auth.py` calls `get_current_user.__wrapped__` to access
the underlying coroutine directly (bypassing FastAPI's DI system). If the
dependency is not decorated with `@functools.wraps`, `__wrapped__` may not
exist. An alternative is to use FastAPI's `TestClient` with overridden
dependencies instead.

### 4. Supabase Google OAuth redirect URI

The `GoogleSignInButton` constructs the OAuth redirect URI as
`{origin}/auth/callback?next={redirectTo}`. A Next.js route handler must
exist at `/auth/callback/route.ts` to exchange the OAuth code for a
session. This callback route is not explicitly listed in Tasks 1.1–1.6
but is required for Google OAuth to complete. Add it in Phase 1 follow-up
or Task 4 frontend polish.

### 5. Dashboard layout stub

`src/frontend/app/(dashboard)/layout.tsx` is not implemented in Phase 1
(it belongs to Task 4.2). The settings page at `/dashboard/settings` will
render without the sidebar/topnav until Phase 4.
