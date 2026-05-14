# Environment Setup Guide

## Prerequisites

- Docker Desktop running
- Terminal access to `src/` directory

Project root: `/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/`

---

## Credential Status

### ✅ Set and working
| Variable | File | Value |
|----------|------|-------|
| `SECRET_KEY` | `backend/.env` | Generated 64-char hex |
| `SUPABASE_URL` | `backend/.env` | `https://feoohtmphywquwzonpwq.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `backend/.env` | *(in .env gesetzt)* |
| `NEXT_PUBLIC_SUPABASE_URL` | `frontend/.env` | `https://feoohtmphywquwzonpwq.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `frontend/.env` | `sb_publishable_WM27…` |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | `frontend/.env` | `pk.eyJ1…` |
| `CELERY_BROKER_URL` | `backend/.env` | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | `backend/.env` | `redis://localhost:6379/1` |

### ⚠️ Needs correction
| Variable | File | Issue |
|----------|------|-------|
| `SUPABASE_JWT_SECRET` | `backend/.env` | Wrong value — a JWT was pasted, but this field needs the **signing secret** (random string from Supabase dashboard → Settings → API → JWT Secret) |

### 🔲 Not yet set (blocks features)
| Variable | File | Where to get |
|----------|------|-------------|
| `SENTINEL_HUB_CLIENT_ID/SECRET/INSTANCE_ID` | `backend/.env` | apps.sentinel-hub.com/dashboard |
| `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | `backend/.env` | AWS IAM |
| `SENDGRID_API_KEY` | `backend/.env` | app.sendgrid.com/settings/api_keys |
| `STRIPE_*` | backend + frontend | dashboard.stripe.com (Phase 5) |

---

## How to start the stack

```bash
cd "/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/src"
docker compose up --build
```

**First time only** — run migrations after postgres is healthy:

```bash
docker compose exec backend alembic upgrade head
```

---

## Service URLs (local)

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| PostgreSQL | localhost:5432 (user: `agrolens`, pass: `localdevpass123`) |
| Redis | localhost:6379 |

---

## Useful commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f celery_worker

# Run new migration
docker compose exec backend alembic upgrade head

# Access DB directly
docker compose exec postgres psql -U agrolens -d agrolens_dev

# Restart single service after code change
docker compose restart backend

# Full reset (deletes all data)
docker compose down -v && docker compose up --build
```

---

## .gitignore note

`backend/.env` and `frontend/.env` are in `.gitignore`. Never commit them. Commit only the `.env.example` files with placeholder values.
