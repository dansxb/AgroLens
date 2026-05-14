# System Overview

## Services (docker-compose)

| Service | Image | Port | Role |
|---------|-------|------|------|
| `postgres` | postgis/postgis:15-3.4 | 5432 | Primary DB with PostGIS |
| `redis` | redis:7-alpine | 6379 | Celery broker + result backend |
| `backend` | python:3.11-slim | 8000 | FastAPI app |
| `celery_worker` | (same as backend) | — | Background task worker |
| `celery_beat` | (same as backend) | — | Periodic task scheduler |
| `frontend` | node:20-alpine | 3000 | Next.js dashboard |

## Directory structure

```
src/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI routers
│   │   ├── core/             # Config, security, rate limiting
│   │   ├── db/               # Session, base class, model registry
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Business logic (S3, SendGrid, exports)
│   ├── alembic/versions/     # DB migrations 0001–0006
│   ├── templates/email/      # SendGrid HTML templates
│   └── worker/tasks/         # Celery tasks
├── frontend/
│   ├── app/(dashboard)/      # Next.js app router pages
│   ├── components/           # React components
│   └── lib/                  # API clients, Mapbox helpers
└── ml/
    ├── zones/                # Delineation + zone filter
    └── prescription/         # Rate computation engine
```

## Request flow

```
Browser → Next.js (3000) → FastAPI (8000) → PostgreSQL
                                          → S3 (rasters)
                                          → Celery → Redis
```

## Auth flow

Supabase Auth (JWT HS256) → `app/core/security.py` → lazy user provisioning in `deps.py`  
API key fallback: `get_current_user_or_key()` → bcrypt verify → `ApiKey` table

## Related notes

- [[Architecture/Data Model]]
- [[Architecture/ML Pipeline]]
- [[Architecture/API Endpoints]]
