# AgroLens

> Precision agriculture SaaS — satellite-driven Variable Rate Application maps for arable farming.

## Quick Links

- [[Project/Overview]] — What AgroLens is, tech stack, goals
- [[Tasks/Phase 4 Board]] — Phase 4 complete ✅
- [[Tasks/Phase 5 Board]] — Phase 5 plan (Stripe billing)
- [[Dev Log/Index]] — Chronological changelog
- [[Architecture/System Overview]] — Services, data flow, DB schema
- [[Architecture/API Endpoints]] — Full REST endpoint reference
- [[Dev Setup/Environment Setup]] — Credentials status + docker commands
- [[Dev Setup/Testing Guide]] — Step-by-step first test
- [[Memory/Context]] — Working context for Claude sessions

## Agent Reference Docs

- [[Agents/CEO Research]] — Market data, competitors, EU regulation trends
- [[Agents/Planner Reference]] — Sentinel Hub API, Stripe flow, Supabase JWT claims
- [[Agents/Developer Reference]] — AsyncSession, Celery, Next.js, Mapbox, known gotchas
- [[Agents/Checker Reference]] — §67 PflSchG fields, ISOXML structure, GDPR/Data Act

## Architecture Decisions (ADR)

- [[Architecture/Decisions/ADR-001 PgEnum statt sa.Enum]] — Warum niemals `sa.Enum`
- [[Architecture/Decisions/ADR-002 AsyncSession Pattern]] — Session-Sharing-Regeln, Celery sync
- [[Architecture/Decisions/ADR-003 TASKDATA.XML ist Pflicht]] — ISOBUS-Kompatibilität
- [[Architecture/Decisions/ADR-004 Supabase JWT Verification]] — JWT Secret vs. Service Role Key

## Memory (Claude-intern)

- [[Memory/Context]] — Projektstand + Key Rules (auto-geladen bei Session-Start)
- [[Memory/Quick Reference]] — Dichte Lookup-Tabelle (auto-geladen bei Session-Start)
- [[Memory/Session Changes]] — Automatisch geloggte Dateiänderungen dieser Session

## Status

| Phase | Status |
|-------|--------|
| Phase 0 — Infrastructure | ✅ Complete |
| Phase 1 — Core Models + Auth | ✅ Complete |
| Phase 2 — Imagery Pipeline | ✅ Complete |
| Phase 3 — Zones + Prescriptions | ✅ Complete |
| Phase 4 — Farmer Dashboard | ✅ Complete |
| Phase 5 — Billing + Subscriptions | 🔲 Not started |

## Stack

**Backend:** FastAPI · SQLAlchemy 2 · PostGIS · Alembic · Celery + Redis · SendGrid · Stripe  
**Frontend:** Next.js 14 · Tailwind CSS · Mapbox GL JS · Recharts · Supabase Auth  
**Infra:** Docker Compose · PostgreSQL 15 · S3 · Sentry · next-pwa
