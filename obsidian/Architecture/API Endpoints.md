# API Endpoints Reference

Base URL (local): `http://localhost:8000`  
All protected endpoints require: `Authorization: Bearer <supabase_jwt>`  
API key auth: `Authorization: Bearer agro_sk_<32chars>` (alternative to JWT)

---

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Liveness check → `{"status":"ok"}` |

---

## Auth (Supabase-managed — no backend routes)

Login, signup, and session refresh are handled entirely by Supabase Auth SDK on the frontend. The backend only verifies the JWT on each request.

---

## Farms

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/farms` | JWT | Create farm |
| GET | `/api/v1/farms` | JWT | List farms for current user |
| GET | `/api/v1/farms/{id}` | JWT | Get farm by ID |
| PUT | `/api/v1/farms/{id}` | JWT | Update farm |
| DELETE | `/api/v1/farms/{id}` | JWT | Delete farm |

---

## Fields

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/fields` | JWT | Create field (GeoJSON polygon) |
| GET | `/api/v1/fields` | JWT | List all fields (all farms) |
| GET | `/api/v1/fields/{id}` | JWT | Get field + geometry |
| PUT | `/api/v1/fields/{id}` | JWT | Update field metadata |
| DELETE | `/api/v1/fields/{id}` | JWT | Delete field |

---

## Vegetation Indices (NDVI / NDRE)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/fields/{id}/vegetation-indices` | JWT | Trigger Sentinel-2 pull for date range |
| GET | `/api/v1/fields/{id}/vegetation-indices` | JWT | List computed indices |

---

## NDVI Composites

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/fields/{id}/composites` | JWT | List all composites |
| GET | `/api/v1/fields/{id}/composites/latest` | JWT | Latest composite + stats |

---

## Prescriptions (VRA Maps)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/fields/{id}/prescriptions` | JWT | Generate VRA prescription from latest composite |
| GET | `/api/v1/fields/{id}/prescriptions` | JWT | List prescriptions |
| GET | `/api/v1/fields/{id}/prescriptions/{pid}` | JWT | Get prescription + zone GeoJSON |
| GET | `/api/v1/fields/{id}/prescriptions/{pid}/export/shapefile` | JWT | Download Shapefile (.zip) |
| GET | `/api/v1/fields/{id}/prescriptions/{pid}/export/taskdata` | JWT | Download ISOXML TASKDATA.XML |
| GET | `/api/v1/fields/{id}/prescriptions/{pid}/export/pdf` | JWT | Download PDF report |

---

## Notification Preferences

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/notification-preferences` | JWT | List preferences for user |
| PUT | `/api/v1/notification-preferences/{id}` | JWT | Toggle enabled/disabled |

---

## API Keys

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/api-keys` | JWT | Create key — returns full `agro_sk_…` once |
| GET | `/api/v1/api-keys` | JWT | List keys (prefix + name only, no hash) |
| DELETE | `/api/v1/api-keys/{id}` | JWT | Revoke key |

---

## Account

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/account/usage` | JWT or API Key | Hectares used / plan limit / usage % |

---

## Monitoring (internal)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/monitoring/pipeline-health` | `X-Monitor-Secret` header | Pipeline health check for ops |

---

## Billing (Phase 5 — stubs, not yet implemented)

| Method | Path | Notes |
|--------|------|-------|
| POST | `/api/v1/billing/checkout` | Stripe checkout session |
| POST | `/api/v1/billing/portal` | Stripe customer portal |
| POST | `/api/v1/webhooks/stripe` | Stripe webhook receiver |

---

## Interactive Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
