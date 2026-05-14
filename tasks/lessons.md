# AgroLens — Lessons Learned

## SQLAlchemy Enum

**Rule:** Always use `PgEnum` from `sqlalchemy.dialects.postgresql`, never `sa.Enum(..., create_type=False)`.
`sa.Enum` fires `_on_table_create` regardless of the flag and causes `DuplicateObject` errors on repeated migration runs.

## relationship() comment= kwarg

**Rule:** `relationship()` does not accept `comment=`. That kwarg is only valid on `mapped_column()`.
Passing `comment=` to `relationship()` raises `TypeError` at import time, silently breaking Alembic.

## Numeric precision for area

**Rule:** Use `Numeric(12, 4)` for area columns. `Numeric(10, 1)` loses sub-hectare precision (0.95 ha rounds to 1.0 ha).

## Account deletion re-authentication

**Rule:** Any destructive account action (account deletion) must call `supabase.auth.signInWithPassword()` in the frontend *before* the API call. A checkbox or "type DELETE" confirmation alone is not sufficient.

## Alembic migration geometry columns

**Rule:** PostGIS geometry columns must be added via `SELECT AddGeometryColumn(...)` raw SQL, not via SQLAlchemy's `Geometry` type in `op.create_table()`. This ensures PostGIS registers the column in its internal metadata tables.

## PgEnum + migrations

**Rule:** Create enum types with `DO $$ BEGIN CREATE TYPE ... EXCEPTION WHEN duplicate_object THEN null; END $$;` in migrations so reruns are idempotent.

## Dockerfile requirements split

**Rule:** Phase 0–1 uses `requirements-core.txt` (no GDAL/torch/rasterio). Phase 2+ uses `requirements.txt`. Switch the Dockerfile builder stage when entering Phase 2.

## ml/ PYTHONPATH in Celery workers

**Rule:** The `ml/` directory is outside `src/backend/` and not on the default PYTHONPATH. Add `- ./ml:/app/ml:cached` volume mount to `celery_worker` and `celery_beat` in `docker-compose.yml`.

## TASKDATA.XML is mandatory for ISOBUS

**Rule:** Shapefiles cannot be loaded by ISOBUS tractor terminals (John Deere, Fendt, CLAAS). Every prescription export must produce both Shapefile (for GIS desktop) AND TASKDATA.XML (ISO 11783-10) for tractor terminals.

## §67 PflSchG documentation

**Rule:** Every prescription output path must have a corresponding `SprayingRecord` model for German plant-protection law compliance. Professional pesticide users in Germany are required to document every application from 2026.

## FLIK-Nummer

**Rule:** The `fields` table must carry a `flik VARCHAR(18)` column for German InVeKoS cross-compliance. It is optional (nullable) but must appear in all exports (PDF, Shapefile DBF, TASKDATA.XML).
