# 2026-05-13 — Phase 4 Complete

## What was built

### Backend

**Task 4.5 — Email Notifications**
- `NotificationPreference` model + migration 0005
- SendGrid email service with single-retry on 5xx
- Two Celery tasks: `send_new_vra_map_notification` (triggered on prescription creation) and `check_stress_alerts` (daily 07:00 UTC, 15% NDVI deviation threshold)
- GET + PUT `/api/v1/notification-preferences`
- German HTML email templates for both notification types

**Task 4.6 — API Keys + Rate Limiting**
- `ApiKey` model + migration 0006 (bcrypt hash, key prefix stored, never plain text)
- Key format: `agro_sk_<32 random chars>`
- POST/GET/DELETE `/api/v1/api-keys` + GET `/api/v1/account/usage`
- slowapi Redis sliding-window rate limiter: 100 req/min per API key
- `get_current_user_or_key()` dep: JWT-first, falls back to API key bcrypt verify

### Frontend (35 files)

**Task 4.1** — Field list (sortable, health badges), GeoJSON/KML upload form, Mapbox Draw polygon tool, field pages

**Task 4.2** — Dashboard layout (CSS grid, 240px sidebar), Sidebar + TopNav + MobileNav (bottom nav on mobile), FieldOverviewMap (all fields color-coded by NDVI health), SummaryPanel (4 stat cards), PlanUsageBar (amber at 80%, red at 95%)

**Task 4.3** — NdviChart (Recharts LineChart with ±σ band), PrescriptionZoneMap (Mapbox satellite basemap, zone legend), ZoneBreakdownTable, ExportButtons (Shapefile / TASKDATA.XML / PDF / GeoJSON clipboard), field detail page with prescription generation modal

**Task 4.4** — next-pwa, PWA manifest (`theme_color: #16a34a`, `display: standalone`), OfflineBanner, cache-first for Mapbox tiles, network-first for API responses

## Bugs fixed during session

1. `npm ci` failing — no `package-lock.json` → Dockerfile changed to `npm install` fallback
2. `rasterio` build failing in Docker — builder stage missing `libgdal-dev`, `libgeos-dev`, `libproj-dev`; also missing `setuptools` → added to Dockerfile
3. `NotificationPreference` model was still a comment stub → wrote full ORM model
4. `VegetationIndex.computed_at` doesn't exist → fixed to `created_at`
5. `S3StorageService` class imported but only module functions existed → added class wrapper
6. `@mapbox/togeojson` import shape wrong → `import { toGeoJSON }` → `import * as toGeoJSON`
7. `require("next-pwa/cache")` sub-path doesn't exist in v5 → removed `runtimeCaching` option
8. Stub route files (billing, webhooks, monitoring) had no `router` export → added empty `APIRouter`

## What's next

Phase 5: Stripe billing, subscription model, usage enforcement.
