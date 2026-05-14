# Phase 4 Tasks

## Pre-flight
- [x] Remove Phase 1 try/except guard from db/base.py
- [x] Add slowapi to requirements.txt
- [x] Add next-pwa to package.json

## Task 4.5 — Email Notifications
- [x] NotificationPreference model
- [x] notification_preference schemas
- [x] notifications.py SendGrid service
- [x] Celery notification tasks
- [x] Notification preferences route
- [x] Email HTML templates (2)
- [x] Migration 0005
- [x] Update beat_schedule.py

## Task 4.6 — API Keys + Rate Limiting
- [x] ApiKey model
- [x] api_key schemas
- [x] api_keys route
- [x] rate_limiting.py
- [x] deps.py API key auth path
- [x] main.py SlowAPI middleware
- [x] Migration 0006
- [x] Remove Phase 4 db/base.py guard

## Task 4.1 — Field Management UI
- [x] lib/api/fields.ts
- [x] lib/mapbox/drawing.ts
- [x] FieldList.tsx
- [x] FieldUploadForm.tsx
- [x] FieldDrawMap.tsx
- [x] fields/page.tsx
- [x] fields/new/page.tsx

## Task 4.2 — Dashboard Home
- [x] dashboard layout.tsx
- [x] Sidebar.tsx
- [x] TopNav.tsx
- [x] FieldOverviewMap.tsx
- [x] SummaryPanel.tsx
- [x] PlanUsageBar.tsx
- [x] dashboard page.tsx

## Task 4.3 — Field Detail
- [x] lib/api/prescriptions.ts
- [x] lib/api/analytics.ts
- [x] NdviChart.tsx
- [x] PrescriptionZoneMap.tsx
- [x] ZoneBreakdownTable.tsx
- [x] ExportButtons.tsx
- [x] fields/[fieldId]/page.tsx

## Task 4.4 — Mobile + PWA
- [x] next.config.js PWA config
- [x] public/manifest.json
- [x] app/layout.tsx SW registration + OfflineBanner
- [x] cache-strategies.ts
- [x] public/sw.js

## Additional files created
- [x] components/layout/MobileNav.tsx (bottom nav for mobile)
- [x] components/OfflineBanner.tsx (offline detection banner)

## Wrap-up
- [ ] Update docs/dev-log.md
- [x] Update tasks/todo.md results section

## Results

### Backend
- 2 new ORM models: NotificationPreference, ApiKey
- 2 Alembic migrations: 0005 (notification_preferences), 0006 (api_keys)
- SendGrid email service with single-retry logic
- 2 Celery tasks: send_new_vra_map_notification, check_stress_alerts (daily 07:00 UTC)
- GET/PUT /api/v1/notification-preferences
- POST/GET/DELETE /api/v1/api-keys + GET /api/v1/account/usage
- slowapi SlowAPI middleware registered; 100 req/min per API key
- get_current_user_or_key() in deps.py: JWT-first, falls back to bcrypt API key verify
- Phase 4 db/base.py guard removed

### Frontend (35 files implemented)
- Task 4.1: full field management UI (list, upload form, draw map, pages)
- Task 4.2: dashboard layout (sidebar + topnav + mobile nav), field overview map, summary panel, plan usage bar
- Task 4.3: NDVI chart (Recharts), prescription zone map (Mapbox), zone breakdown table, export buttons, field detail page with prescription modal
- Task 4.4: next-pwa config, PWA manifest, OfflineBanner, cache-strategies.ts, custom sw.js
