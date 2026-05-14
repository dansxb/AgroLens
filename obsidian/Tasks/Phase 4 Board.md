# Phase 4 Task Board

## ✅ Done

### Pre-flight
- [x] Remove Phase 1 try/except guard from `db/base.py`
- [x] Add `slowapi==0.1.*` to `requirements.txt`
- [x] Add `next-pwa: ^5.6.0` to `package.json`

### Task 4.5 — Email Notifications
- [x] `NotificationPreference` ORM model
- [x] `notification_preference` Pydantic schemas
- [x] `services/notifications.py` — SendGrid, retries once on 5xx
- [x] `worker/tasks/notifications.py` — `send_new_vra_map_notification` + `check_stress_alerts`
- [x] `api/routes/notification_preferences.py` — GET + PUT
- [x] `templates/email/new_vra_map.html` + `field_stress_alert.html`
- [x] Migration 0005
- [x] `beat_schedule.py` — daily stress check at 07:00 UTC

### Task 4.6 — API Keys + Rate Limiting
- [x] `ApiKey` ORM model
- [x] `api_key` schemas (create / read / created-once)
- [x] `api/routes/api_keys.py` — POST/GET/DELETE + `GET /account/usage`
- [x] `core/rate_limiting.py` — slowapi, 100 req/min per API key
- [x] `api/deps.py` — `get_current_user_or_key()` (JWT → API key fallback)
- [x] `main.py` — SlowAPI middleware registered
- [x] Migration 0006
- [x] Phase 4 `db/base.py` guard removed

### Task 4.1 — Field Management UI
- [x] `lib/api/fields.ts`
- [x] `lib/mapbox/drawing.ts`
- [x] `FieldList.tsx`, `FieldUploadForm.tsx`, `FieldDrawMap.tsx`
- [x] `fields/page.tsx`, `fields/new/page.tsx`

### Task 4.2 — Dashboard Home
- [x] `app/(dashboard)/layout.tsx`
- [x] `Sidebar.tsx`, `TopNav.tsx`, `MobileNav.tsx`
- [x] `FieldOverviewMap.tsx`, `SummaryPanel.tsx`, `PlanUsageBar.tsx`
- [x] `dashboard page.tsx`

### Task 4.3 — Field Detail
- [x] `lib/api/prescriptions.ts`, `lib/api/analytics.ts`
- [x] `NdviChart.tsx` (Recharts + ±σ band)
- [x] `PrescriptionZoneMap.tsx` (Mapbox satellite)
- [x] `ZoneBreakdownTable.tsx`, `ExportButtons.tsx`
- [x] `fields/[fieldId]/page.tsx` (prescription modal)

### Task 4.4 — Mobile + PWA
- [x] `next.config.js` — next-pwa
- [x] `public/manifest.json`
- [x] `OfflineBanner.tsx`
- [x] `lib/service-worker/cache-strategies.ts`
- [x] `public/sw.js`

## 🔲 Up Next — Phase 5

- [ ] `Subscription` ORM model
- [ ] Stripe checkout + portal endpoints
- [ ] Stripe webhook handler
- [ ] Subscription-gated field limits
- [ ] `GET /account/usage` — real plan_limit from Subscription

## Notes

- `billing.py`, `webhooks.py`, `monitoring.py` routes are stub routers (Phase 5)
- `app.worker.tasks.billing` registered in Celery but empty (no error)
- Phase 5 Subscription model guarded by `try/except` in `db/base.py`
