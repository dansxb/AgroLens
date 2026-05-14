# Claude Working Context

This note mirrors the persistent memory Claude uses across sessions. Update after each session.

## About Daniel

- Building AgroLens — precision agriculture SaaS for German farmers
- Works with Claude Code in VS Code extension
- Prefers concise responses, no trailing summaries
- Communicates in German when discussing the product, English for technical work

## Project state (as of 2026-05-13)

Phases 0–4 complete. Phase 5 (Stripe billing, subscriptions) is next.

**Session 2026-05-13 fixes applied:**
- Docker build fix: rasterio `--no-build-isolation` (pip 26 isolated build env bug)
- Bug fix: `settings.SENDGRID_API_KEY` → `settings.sendgrid_api_key` (Pydantic lowercase)
- Error handling + logging added: analytics.py, notification_preferences.py, exports.py, worker/tasks/notifications.py
- New agent: `debug-spezialist` — spawnable on-demand for bug diagnosis, documents in `docs/debug-log.md`

After first build, run: `docker compose exec backend alembic upgrade head`

### Agent-Team (6 Agenten)

| Agent | Datei | Aufgabe |
|---|---|---|
| `ceo` | `.claude/agents/ceo.md` | Strategie, Marktforschung |
| `planner` | `.claude/agents/planner.md` | Tasks aus CEO-Zielen |
| `software-developer` | `.claude/agents/software-developer.md` | Implementierung |
| `checker` | `.claude/agents/checker.md` | Code-Review, Security |
| `landwirt-validator` | `.claude/agents/landwirt-validator.md` | §67 PflSchG, ISOBUS |
| `debug-spezialist` | `.claude/agents/debug-spezialist.md` | Bug-Diagnose on-demand |

Debug-Log: `docs/debug-log.md` (nur anhängen)

### Credentials set
- `SECRET_KEY` — generated ✅
- `SUPABASE_URL` — `https://feoohtmphywquwzonpwq.supabase.co` ✅
- `SUPABASE_SERVICE_ROLE_KEY` — set ✅
- `NEXT_PUBLIC_SUPABASE_URL` — set ✅
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — set ✅
- `NEXT_PUBLIC_MAPBOX_TOKEN` — set ✅
- `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` — fixed (no bogus password) ✅
- `SUPABASE_JWT_SECRET` — correct signing secret set ✅

## Key rules Claude must follow

### Python / Backend
- Always use `PgEnum` from `sqlalchemy.dialects.postgresql` — NEVER `sa.Enum` (causes DuplicateObject errors)
- `create_type=False` on all PgEnum instances in models
- `relationship()` must NOT have `comment=` kwarg (raises TypeError)
- PostGIS geometry columns added via `SELECT AddGeometryColumn(...)` in migrations, not inline
- Read every file with the Read tool before using Write — Write fails on unread files
- Use `get_db` (not `get_async_db`) as the async DB dependency name

### Frontend / TypeScript
- `import * as toGeoJSON from "@mapbox/togeojson"` — NOT named import
- next-pwa v5 does not have a `/cache` sub-path
- `@/components/*`, `@/lib/*` etc. all resolve correctly via tsconfig paths

### Workflow (CLAUDE.md)
- Enter plan mode for any task with 3+ steps
- Track progress in `tasks/todo.md`
- Write lessons to `tasks/lessons.md` after any correction
- Never mark a task complete without verifying it works
- Update this Obsidian vault at the end of each session
- **Landwirt-Validator runs after every phase** — alongside the Checker, before any phase is marked complete. Agent file: `.claude/agents/landwirt-validator.md`. Report goes to `docs/landwirt-validator-report.md`.

## Environment

- Project root: `/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/`
- Obsidian vault: `/Users/danielschaller/Documents/AgroLens/`
- Claude memory files: `~/.claude/projects/-Users-danielschaller-Desktop-CS-Haus---Garten-Winter--Claude-Agents/memory/`
