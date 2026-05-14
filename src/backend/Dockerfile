# ============================================================
# AgroLens Backend — Multi-stage Dockerfile
# Base image: Python 3.11-slim
# Includes GDAL system dependencies for rasterio & geopandas
# ============================================================

# -----------------------------------------------------------
# Stage 1: system dependency builder
# Installs GDAL, GEOS, PROJ and compiles any C extensions
# -----------------------------------------------------------
FROM python:3.11-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system libraries required to compile rasterio, geopandas, and psycopg2.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    gdal-bin \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY requirements.txt .

# rasterio 1.3.x has no ARM64 wheel — must build from source. pip 26 isolated build
# envs lack pkg_resources, breaking the source build. Strategy:
#   1. Pre-install build deps (setuptools<81, Cython<3, numpy) into main env
#   2. Build the rasterio wheel once with --no-build-isolation, cache in /wheelhouse
#   3. Install requirements.txt with --find-links=/wheelhouse so pip uses the cached
#      wheel instead of triggering a second isolated-env build (which would fail again)
RUN pip install "setuptools<81" "Cython<3" "numpy==1.26.*" pip --upgrade && \
    pip wheel --no-build-isolation --no-deps --wheel-dir=/wheelhouse rasterio==1.3.11 && \
    CFLAGS="-Wno-incompatible-pointer-types" \
        pip wheel --no-build-isolation --no-deps --wheel-dir=/wheelhouse "fiona==1.9.*" && \
    pip install --prefix=/install --find-links=/wheelhouse --prefer-binary -r requirements.txt


# -----------------------------------------------------------
# Stage 2: development image
# Hot-reloads source via volume mount, includes dev tools
# -----------------------------------------------------------
FROM python:3.11-slim AS development

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Runtime libs including GDAL/GEOS/PROJ for rasterio & geopandas (Phase 2+)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user for security
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# In development the source is mounted as a volume, so we only
# copy the requirements as a cache hint; actual code is mounted at runtime
COPY --chown=appuser:appgroup requirements.txt .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]


# -----------------------------------------------------------
# Stage 3: production image
# Copies source code; runs as non-root; no dev tools
# -----------------------------------------------------------
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Runtime libraries only — stable names work on AMD64 and ARM64
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled Python packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --no-create-home appuser

WORKDIR /app

# Copy application source (no secrets — all via env vars at runtime)
COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
