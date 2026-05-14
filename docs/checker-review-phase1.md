# Checker Review — Phase 1
**Date**: 2026-05-12
**Overall Status**: NEEDS CHANGES

---

## Summary

Phase 1 delivers a solid, mostly production-quality implementation of user/farm/field models, JWT-protected CRUD endpoints, Alembic migration, and frontend auth pages. Security fundamentals are correctly implemented: JWT signature and expiry are fully verified (not just decoded), ownership is enforced on every farm and field endpoint via `user_id` JOIN/filter, all SQL uses the SQLAlchemy ORM with no string interpolation, and no secrets are hardcoded in source files. However, two bugs were fixed directly by the Checker (broken `__wrapped__` calls in test_auth.py; unused `Metadata` import in a `"use client"` component), one plan-required acceptance criterion is missing from the DELETE /me flow (password re-authentication), and several medium-severity issues in code quality and architecture require developer attention before Phase 2 begins.

---

## Issues Found

| # | Severity | File | Issue | Required Fix |
|---|----------|------|-------|--------------|
| 1 | CRITICAL | `src/backend/tests/test_auth.py` lines 140, 170 | Both `get_current_user` tests call `get_current_user.__wrapped__(...)`, but `get_current_user` in `deps.py` is a plain `async def` with no `@functools.wraps` decorator. `__wrapped__` does not exist on it; both tests would raise `AttributeError` at runtime, meaning they have never been executed and cannot be trusted as green. **Fixed by Checker**: replaced `.__wrapped__(jwt_payload, mock_db)` with a direct keyword-argument call `await get_current_user(payload=jwt_payload, db=mock_db)`. | FIXED — verify tests pass with `pytest tests/test_auth.py -v`. |
| 2 | CRITICAL | `src/frontend/app/(auth)/login/page.tsx` line 19 | `import type { Metadata } from "next"` in a `"use client"` component. `Metadata` is a server-side Next.js export type that cannot be used in client components; it is not referenced anywhere in this file. Under TypeScript strict mode with `isolatedModules: true`, unused type imports do not cause a compile error but will be flagged by ESLint (and are a lint failure in most CI pipelines). More importantly, it signals the developer may have intended to export metadata from a client component, which is an architectural error in Next.js 14. **Fixed by Checker**: removed the unused import. | FIXED. |
| 3 | HIGH | `src/backend/app/api/routes/users.py` + `src/frontend/components/settings/DeleteAccountDialog.tsx` | Development-plan Task 1.6 acceptance criterion explicitly states: "`DELETE /api/v1/users/me` requires password re-authentication before deletion (Supabase re-auth flow)." Neither the backend route nor the frontend dialog implements this. The dialog only requires typing the word "DELETE" — there is no call to `supabase.auth.reauthenticate()` or `signInWithPassword()` before the delete. This is both a plan-alignment failure and a security gap: a stolen JWT (e.g., from an XSS attack) is sufficient to permanently delete the account without any additional user action. | Developer must add a password confirmation step to the delete dialog (call `supabase.auth.signInWithPassword({ email, password })` before the DELETE API call) and document any intentional deviation in `docs/blockers.md` if Supabase re-auth is unavailable in the current config. |
| 4 | MEDIUM | `src/backend/app/models/field.py` line 103 + `src/backend/alembic/versions/0001_create_users_farms_fields.py` line 211 + `src/backend/app/api/routes/fields.py` line 66 | `area_ha` is stored as `Numeric(10, 1)` (1 decimal place) and the API rounds to 1 decimal place (`round(area or 0.0, 1)`). This means a 0.05 ha (500 m²) field is stored as 0.1 ha — a 100% relative error. Many European arable fields are 1–20 ha, so this is adequate for typical use; but vegetable plots, polytunnels, or test polygons can be <0.1 ha. The spec says `Numeric(10, 1)` in the plan but this should be flagged as a known limitation. | Change `Numeric(10, 1)` to `Numeric(12, 4)` in the ORM model and a corresponding `ALTER COLUMN` migration, and change `round(..., 1)` to `round(..., 4)` in the route. Alternatively, document the 1-decimal precision limit as an intentional product decision in `docs/blockers.md`. Requires a new Alembic migration if changed. |
| 5 | MEDIUM | `src/backend/app/api/routes/users.py` line 135 | `response.text` from a failed Supabase Admin API call is logged at `logger.error(...)`. This is server-side only and does not reach the HTTP response (the response returns a generic "Failed to delete user from authentication provider." message), so this is not a client-facing data leak. However, `response.text` may contain Supabase error details (including internal identifiers) that should not appear in application logs at ERROR level without sanitisation. Low-risk in practice but worth noting. | Consider logging only `response.status_code` at ERROR level and truncating or omitting `response.text`, or log it at DEBUG level only. |
| 6 | MEDIUM | `src/backend/app/schemas/farm.py` — `FarmRead` | `FarmRead` exposes `created_at` but omits `updated_at`. Clients cannot tell when a farm was last modified. Both `user.py` schemas and the `FieldRead` schema also omit `updated_at`. This is a minor API completeness gap that may require a frontend display later. | Add `updated_at: Optional[datetime] = None` to `FarmRead`, `FieldRead`, and `UserRead`. No migration required — column already exists in all three tables. |
| 7 | MEDIUM | `src/backend/tests/test_auth.py` | The five tests in this file cover `verify_supabase_jwt` and `get_current_user` in isolation. There are no integration tests for the farm/field endpoints (e.g., `GET /api/v1/farms` with a valid JWT returns 200; without a JWT returns 401). The dev-log references `tests/test_fields_api.py` as implemented, but that file was not in the Phase 1 file list provided to the Checker. If it exists, it should be verified. | Provide `tests/test_fields_api.py` for Checker review in Phase 2, or include it in the Phase 1 scope as originally described in the dev-log. |
| 8 | LOW | `src/backend/app/models/user.py` lines 87, 93 | `created_at` and `updated_at` are typed `Mapped[Optional[object]]` instead of `Mapped[Optional[datetime]]`. The same pattern appears in `farm.py` (lines 60, 65) and `field.py` (lines 111, 117, 93). Using `object` disables all type checking on these columns — mypy will accept any operation on them. The `Farm` model similarly uses `Mapped[Optional[object]]` for timestamp columns. | Import `datetime` from the standard library and use `Mapped[Optional[datetime]]` for all timestamp columns. The `planting_date` column in `field.py` (line 93) should use `Mapped[Optional[date]]`. |
| 9 | LOW | `src/frontend/app/(auth)/login/page.tsx` | No `export const metadata` block — while this cannot be added to a `"use client"` component directly, the parent `(auth)/layout.tsx` should export metadata for the login page (page title, description for SEO). Not a functional issue, but relevant for production. | Add metadata to `src/frontend/app/(auth)/layout.tsx` if not already present. Not blocking. |
| 10 | LOW | `src/frontend/hooks/useAuth.ts` — session expiry | `useAuth` handles session expiry correctly via `onAuthStateChange` (when the token expires Supabase fires a `SIGNED_OUT` or `TOKEN_REFRESHED` event and the hook updates state). However, there is no explicit handling of the `TOKEN_REFRESH_ERROR` event — if the refresh fails silently (e.g., network down), the hook will show the user as logged in with an expired session until the next navigation triggers middleware. This is a known Supabase client limitation; document it as a known issue. | Handle `_event === "TOKEN_REFRESH_ERROR"` in `onAuthStateChange`: call `setUser(null)` and `setSession(null)` so the UI reflects the expired state. Low priority. |
| 11 | LOW | `src/backend/app/db/base.py` | The Phase 0 Checker recommended renaming `_e` to `_exc` for consistency. This was not addressed. Minor style issue, not blocking. | Rename `_e` to `_exc` in all five `except ImportError as _e:` clauses. |

---

## Fixes Applied Directly

### Fix 1 — `src/backend/tests/test_auth.py` (CRITICAL)

**Problem**: `test_get_current_user_creates_new_user` and `test_get_current_user_returns_existing_user` called `get_current_user.__wrapped__(jwt_payload, mock_db)`. `get_current_user` is a plain `async def` with no `@functools.wraps` wrapper; `__wrapped__` does not exist and would raise `AttributeError` at test collection time, silently skipping both tests (or crashing the test session depending on pytest version).

**Fix applied**: Replaced both `__wrapped__` calls with direct async function calls using keyword arguments:
```python
# Before (broken):
user = await get_current_user.__wrapped__(jwt_payload, mock_db)

# After (correct):
user = await get_current_user(payload=jwt_payload, db=mock_db)
```

This matches the actual function signature `async def get_current_user(payload: Dict[str, Any] = Depends(...), db: AsyncSession = Depends(...))`.

### Fix 2 — `src/frontend/app/(auth)/login/page.tsx` (CRITICAL)

**Problem**: `import type { Metadata } from "next"` at line 19 in a `"use client"` component. `Metadata` is never used in the file body. This would fail ESLint (`@typescript-eslint/no-unused-vars` or `import/no-unused-vars`), and importing server types in client components can cause build errors in some Next.js 14 configurations.

**Fix applied**: Removed the unused import entirely.

---

## Feedback to Software-Developer

Overall, the Phase 1 implementation is architecturally correct and production-quality in its core functionality. The JWT verification correctly calls `jwt.decode()` with `algorithms=[_ALGORITHM]` and checks expiry via `ExpiredSignatureError` — it does not just decode without verification. Ownership enforcement is correctly implemented in both farms and fields via `user_id` filters and JOIN conditions. The PostGIS geometry pipeline (ST_GeomFromGeoJSON, ST_AsGeoJSON, ST_Area/ST_Transform) is correctly wired.

Specific items to address before Phase 2 begins:

1. **REQUIRED (Issue #3)**: Implement password re-authentication on account deletion as specified in the Task 1.6 acceptance criteria. The current dialog only requires typing "DELETE" — it must also require the user's password and call `supabase.auth.signInWithPassword()` before the API delete call.

2. **REQUIRED (Issue #4)**: Decide on `area_ha` precision and either document the 1-decimal-place limitation explicitly or migrate to `Numeric(12, 4)`. The current precision is inadequate for small-plot agriculture.

3. **VERIFY (Issue #1, now fixed)**: Run `pytest tests/test_auth.py -v` to confirm the fixed tests pass. The previous `__wrapped__` calls were silently broken — the tests were never actually exercising `get_current_user`.

4. **Code quality (Issue #8)**: Replace all `Mapped[Optional[object]]` with `Mapped[Optional[datetime]]` / `Mapped[Optional[date]]` in the three model files. mypy cannot provide type safety on `object`-typed columns.

5. **Missing `updated_at` in schemas (Issue #6)**: Add `updated_at` to `FarmRead`, `FieldRead`, and `UserRead` so clients can display last-modified timestamps.

6. **Provide `test_fields_api.py` for review (Issue #7)**: The dev-log claims this file was implemented but it was not included in the Checker's review scope. Include it in the next handoff.

---

## What Must Be Fixed Before Running the Migration

Nothing — the migration (`0001_create_users_farms_fields.py`) is safe to run as written. Specifically:

- `revision`, `down_revision`, `branch_labels`, and `depends_on` are all declared.
- `upgrade()` and `downgrade()` are fully implemented (not stubs).
- `CREATE EXTENSION IF NOT EXISTS postgis` is present (idempotent).
- The `fields` geometry column has a GIST spatial index (`ix_fields_geometry_gist`).
- `downgrade()` drops tables in correct reverse dependency order: fields → farms → users, then drops the `croptype` enum.
- The `croptype` enum creation is guarded with `DO $$ BEGIN ... EXCEPTION WHEN duplicate_object THEN null; END $$` making it idempotent.
- Running the migration twice is safe: Alembic tracks applied revisions in `alembic_version`; the PostGIS extension and enum creation are individually idempotent.

**Run**: `cd src/backend && alembic upgrade head`

---

## What Must Be Fixed Before Phase 2 Can Begin

1. **Password re-authentication on DELETE /me (Issue #3, REQUIRED)**: The Task 1.6 acceptance criterion is unmet. Either implement the Supabase re-auth flow in the frontend dialog, or document a formal deviation with rationale in `docs/blockers.md` and get sign-off from the project lead.

2. **Verify test suite runs green (Issue #1, now fixed)**: Run `pytest tests/test_auth.py -v` and confirm all 5 tests pass with the `__wrapped__` fix applied. Screenshot or paste output into `docs/dev-log.md` as evidence.

3. **`area_ha` precision decision (Issue #4, REQUIRED)**: Either change `Numeric(10, 1)` to `Numeric(12, 4)` (requires a new Alembic migration) or document the 1 d.p. precision limit as an accepted product constraint in `docs/blockers.md`. Phase 2 will add satellite-derived per-pixel statistics that reference `area_ha` for density calculations — coarse precision at that point becomes a data quality issue.

Once items 1–3 are resolved, Phase 2 may proceed.
