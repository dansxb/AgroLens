-- ============================================================
-- AgroLens — PostgreSQL Initialisation Script
-- Runs automatically on first container startup via
-- docker-entrypoint-initdb.d/
-- ============================================================

-- Enable PostGIS spatial extension (provides geometry types,
-- spatial functions like ST_Area, ST_Transform, ST_Intersects)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable PostGIS topology extension (supports topological data models,
-- used for zone boundary operations)
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable uuid-ossp for UUID generation in migrations
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for password hashing utilities
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Verify PostGIS is installed (this will appear in docker logs)
DO $$
BEGIN
    RAISE NOTICE 'PostGIS version: %', PostGIS_Version();
END
$$;
