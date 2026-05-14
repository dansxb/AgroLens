# First Test Guide

## Before you start — fix this one thing

`SUPABASE_JWT_SECRET` in `src/backend/.env` has the wrong value. A service role JWT was pasted there, but this variable needs the **raw signing secret** — a short random string, not a JWT.

**Get the correct value:**
1. Supabase Dashboard → your project → Settings → API
2. Scroll to **JWT Settings** → copy the **JWT Secret**
3. It looks like: `your-super-secret-jwt-token-with-at-least-32-characters-long` (a plain string, NOT starting with `eyJ`)
4. Paste it into `src/backend/.env` as `SUPABASE_JWT_SECRET=<value>`

Without this, every login attempt will fail with 401.

---

## Step 1 — Build and start

```bash
cd "/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/src"
docker compose up --build
```

Wait until you see all four services healthy:
- `agrolens_postgres` — `healthy`
- `agrolens_redis` — `healthy`
- `agrolens_backend` — logs `Uvicorn running on http://0.0.0.0:8000`
- `agrolens_frontend` — logs `ready - started server on 0.0.0.0:3000`

**First time only** — run migrations in a second terminal:

```bash
cd "/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/src"
docker compose exec backend alembic upgrade head
```

You should see: `Running upgrade ... -> 0006, create_api_keys`

---

## Step 2 — Verify the backend is alive

Open: `http://localhost:8000/health`

Expected response:
```json
{"status": "ok"}
```

Browse all endpoints at: `http://localhost:8000/docs`

---

## Step 3 — Open the app

Open: `http://localhost:3000`

You should see the AgroLens login/signup screen (Supabase Auth UI).

---

## Step 4 — Create your account

1. Click **Sign up**
2. Enter your email and a password
3. Check email for confirmation link and click it
4. You'll be redirected back to `localhost:3000` and logged in

---

## Step 5 — Explore the dashboard

After login you land on the dashboard home:

| What you see | What to look for |
|---|---|
| **Sidebar** | Dashboard / Fields / Settings links |
| **Map (center)** | Mapbox map — should render satellite/street tiles |
| **Summary cards** | 4 stat cards (all zeros — no data yet) |
| **Plan usage bar** | Shows 0% usage |

If the map is blank (no tiles), check the Mapbox token in `frontend/.env`.

---

## Step 6 — Create your first farm and field

The dashboard will be empty until you have a field. Use the API directly for now (UI create-field form is at `/fields/new`):

**Option A — via browser UI:**
1. Click **Fields** in sidebar → **+ New Field**
2. Choose **Upload** tab → upload a `.geojson` file, or
3. Choose **Draw** tab → draw a polygon on the map
4. Fill in field name, crop type, sowing date → Save

**Option B — via Swagger UI (`/docs`):**
1. Click **Authorize** → paste your Supabase JWT (get it from browser devtools → Application → Local Storage → `sb-feoohtmphywquwzonpwq-auth-token` → `access_token`)
2. POST `/api/v1/farms` → create a farm first
3. POST `/api/v1/fields` → create a field with a GeoJSON polygon

---

## Step 7 — Test API keys

1. In Swagger UI (`/docs`) while authorized, call `POST /api/v1/api-keys`
2. Body: `{"name": "test-key"}`
3. Copy the returned `agro_sk_...` key — it's shown only once
4. Use it for subsequent requests: `Authorization: Bearer agro_sk_...`

---

## What works right now vs what needs more credentials

| Feature | Works now |
|---|---|
| Login / signup | ✅ (after JWT secret fix) |
| Map renders | ✅ |
| Dashboard UI | ✅ |
| Field create / list / delete | ✅ |
| API keys | ✅ |
| Rate limiting (100 req/min) | ✅ |
| Account usage endpoint | ✅ |
| Satellite imagery trigger | ❌ needs Sentinel Hub credentials |
| NDVI charts (real data) | ❌ needs Sentinel Hub + AWS |
| Prescription generation | ❌ needs NDVI data first |
| File exports | ❌ needs AWS S3 |
| Email notifications | ❌ needs SendGrid API key |
| Billing / subscriptions | ❌ Phase 5 not built yet |

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Login fails with 401 | `SUPABASE_JWT_SECRET` is wrong — see Step 0 above |
| Map shows blank | `NEXT_PUBLIC_MAPBOX_TOKEN` wrong or expired |
| `alembic upgrade` fails | Docker postgres not healthy yet — wait 30s and retry |
| Backend crashes on start | Check `docker compose logs backend` for import errors |
| Frontend shows blank page | Check `docker compose logs frontend` for compile errors |
| Can't reach `localhost:3000` | Frontend container still building — wait for "ready" log line |
