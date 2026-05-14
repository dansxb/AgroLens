# Checker Review — Phase 0
**Date**: 2026-05-12
**Overall Status**: NEEDS CHANGES

---

## Summary

Phase 0 delivers a solid infrastructure skeleton: the FastAPI and Next.js application shells are well-structured, configuration management is correct, security fundamentals (JWT verification, CORS per-origin, secrets in env vars) are properly implemented, and the `.gitignore` comprehensively covers all secret files. However, two issues required immediate fixes that were applied directly by the Checker before this report was written: (1) `app/db/base.py` would have crashed at import time because it attempted to eagerly import class names from stub model files that contain only a one-line comment, and (2) the `backend/.env.example` contained the well-known AWS documentation example credentials (`AKIAIOSFODNN7EXAMPLE` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`) which trigger secret-scanning tools on every CI provider. Beyond these two items — now fixed — there are a small number of MEDIUM and LOW quality issues to address before or during Phase 1.

---

## Issues Found

| # | Severity | Agent | File | Issue | Required Fix |
|---|----------|-------|------|-------|--------------|
| 1 | CRITICAL | Developer | `src/backend/app/db/base.py` | Eager `from app.models.X import X` imports across all 5 phases would raise `ImportError: cannot import name 'User' from 'app.models.user'` at startup because every model file is a 1-line comment stub. This would break `alembic upgrade head`, `alembic revision --autogenerate`, and any import of `app.db.base`. **Fixed by Checker**: wrapped each phase's import block in `try/except ImportError` with a `logger.debug` fallback. | FIXED — remove guards as each phase's model classes are implemented. |
| 2 | CRITICAL | Developer | `src/backend/.env.example` | `AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE` and `AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` are the canonical AWS documentation example credentials. Every major secret-scanning tool (GitGuardian, truffleHog, GitHub Advanced Security) flags these as real credentials, which will block CI pipelines and potentially trigger false-positive security incidents. **Fixed by Checker**: replaced with `your_aws_access_key_id_here` / `your_aws_secret_access_key_here`. | FIXED. |
| 3 | HIGH | Developer | `src/backend/app/db/base.py` (now fixed) + all phase 1–5 stubs | The dev-log claims `base.py` is "Complete — Central model registry — imports all 12 models for Alembic autogenerate." This statement was misleading: the 12 model files are 1-line stubs with no class definitions, so Alembic autogenerate would find 0 tables. The dev-log should clearly distinguish between "file structure scaffolded (stub)" and "fully implemented". | Developer must update the dev-log to accurately reflect stub vs. implemented status per file. The acceptance criterion for Task 0.5 (alembic upgrade head completes, alembic downgrade -1 works) cannot pass until at least the Phase 1 model stubs become real implementations. Phase 1 can only begin once this is understood and scoped correctly. |
| 4 | MEDIUM | Developer | `src/backend/app/db/session.py` line 95 | `except Exception:` is a bare `Exception` catch (no typed exception, no `as exc`). The plan requirement states "No bare `except:` clauses — exceptions are typed." While technically `except Exception` is typed (vs `except:`), the absence of `as exc` means the exception is silently swallowed before the `raise` — no structured log entry includes the exception details. Contrast with `health.py` line 82 which correctly uses `except Exception as exc:`. | Change to `except Exception as exc:` and add `logger.error("DB session error: %s", exc, exc_info=True)` before the `raise`. |
| 5 | MEDIUM | Developer | `src/backend/app/core/config.py` line 206–209 | `monitor_secret_key` has `default="change_me_in_production"`. A static, well-known default value for a shared secret is a security smell — if a developer forgets to override it, the monitoring endpoint is protected by a trivially guessable key. | Remove the default and make the field required (`...`), or add a startup validator that raises an error if `is_production` and the value equals the default. |
| 6 | MEDIUM | Developer | `src/backend/main.py` line 122 | `allow_headers=["*"]` in the CORS middleware. While `allow_origins` is correctly restricted to `settings.cors_origins`, `allow_headers=["*"]` still allows any request header cross-origin. This is acceptable for development but must be restricted to an explicit allowlist (`["Authorization", "Content-Type", "Accept", "X-Request-ID"]`) before staging or production deployment. | Document this as a required pre-staging task or add a validator in `config.py` that rejects `allow_headers=["*"]` when `is_production`. |
| 7 | MEDIUM | Planner | `docs/development-plan.md` Task 0.5 acceptance criteria | Task 0.5 acceptance criterion states "`alembic upgrade head` from `backend/` directory completes without error". This criterion cannot be verified at end of Phase 0 because no model classes exist. The Planner should have made the Alembic baseline migration (empty schema, no tables) a Phase 0 deliverable, with the model-creating migrations deferred to Phase 1 where the ORM models are actually built. The acceptance criterion as written creates ambiguity about what "Phase 0 complete" means. | Planner should clarify: Task 0.5 acceptance is "baseline (empty) migration applies cleanly"; the first real schema migration is Task 1.3. |
| 8 | LOW | Developer | `src/backend/app/db/session.py` | The `get_db()` dependency catches all exceptions with `except Exception:` (no `as exc`) and re-raises. The `finally: await session.close()` correctly closes the session. The pattern is correct but could be improved by catching `SQLAlchemyError` specifically for database errors vs. re-raising all other exceptions without rollback context. Not blocking. | Consider narrowing to `except SQLAlchemyError as exc:` for rollback-triggering errors; let application-level exceptions (e.g., `HTTPException`) bypass the rollback path. |
| 9 | LOW | Developer | `src/backend/app/db/base.py` (as fixed) | After the Checker's fix, the `try/except ImportError` blocks use a module-level `logger` for `debug` messages. However the logger is defined before `Base` is imported. If `base_class.py` raises on import, the logger is still available — this is fine. Minor: the `_e` variable name is non-standard for exception aliases; convention in this codebase uses `exc`. | Optional: rename `_e` to `_exc` for consistency with the rest of the codebase. |
| 10 | LOW | CEO | `docs/ceo-strategy.md` | The landing page (`page.tsx`) correctly reproduces the headline value proposition, pricing, and Sentinel-2 cost advantage. However, the CEO strategy explicitly lists a **free tier up to 50 ha** as a customer acquisition tool (Risk Mitigation 2, point 3), but the landing page trust signal says "Free up to 50 ha" while the pricing table only shows paid plans (Starter from €49/month). There is no free/trial tier shown in the pricing UI. This is not a technical issue but a go-to-market misalignment. | CEO should decide: is the 50 ha free tier an official plan tier to be added to the pricing table, or is it only an onboarding/trial mechanism handled outside Stripe? Planner needs to know before Task 5.1 (Stripe integration) begins, as it affects the `Subscription.plan` enum. |

---

## Feedback to CEO

No issues found with the strategic document itself — it is comprehensive, well-referenced, and internally consistent. One alignment issue to resolve: the free-tier positioning (50 ha free mentioned in Risk 5 mitigation and in the developer's landing page trust signal) is not reflected in the pricing table in either the strategy document or the landing page. Before Phase 5 (Stripe integration) begins, confirm in writing whether:
1. The free/50 ha tier is a formal plan with a Stripe Free price ID, or
2. It is a time-limited trial (e.g., 30-day free trial on the Starter plan, not a permanent free tier).

The current pricing table in the strategy document has no "Free" row, which means the developer will not build it unless explicitly instructed. The landing page currently implies permanent free access up to 50 ha, which contradicts the pricing table. This discrepancy should be resolved before Phase 5 to avoid rework.

---

## Feedback to Planner

Two issues identified:

1. **Task 0.5 acceptance criterion is unverifiable at Phase 0**: The criterion "`alembic upgrade head` completes without error" requires at least one real model to be registered on `Base.metadata`. Since all models are Phase 1+ deliverables, the Phase 0 Alembic task can only verify that the baseline (empty) migration applies cleanly. This should be stated explicitly in the acceptance criterion to avoid confusion about Phase 0 completion status.

2. **`base.py` scope creep across phases**: Placing a Phase 0 file (`base.py`) that eagerly imports Phase 1–5 model classes creates a hard ordering dependency: `base.py` cannot be "complete" until all future phases are done. The Planner should either: (a) specify that `base.py` starts with only `Base` exported and models are added to it as each phase completes, or (b) specify the stub-guarding pattern (as applied by the Checker) explicitly in Task 0.5 so the developer knows this is intentional. The current plan says "all models registered on `Base.metadata`" which implies completeness from day one — this is architecturally impossible at Phase 0.

No other planning issues found. The phase structure, dependency graph, and task granularity are well-designed.

---

## Feedback to Software-Developer

Strong overall implementation for Phase 0. The infrastructure files that were actually implemented (config.py, security.py, main.py, session.py, health.py, alembic/env.py, page.tsx, client.ts, supabase/client.ts) are production-quality: correct type annotations, Google-style docstrings, proper error handling patterns, and CORS correctly scoped to `ALLOWED_ORIGINS`.

Specific issues to address:

1. **FIXED (Checker action)**: `base.py` eager imports of stub model classes — see Issue #1 above.
2. **FIXED (Checker action)**: AWS documentation example credentials in `.env.example` — see Issue #2 above.
3. **Dev-log accuracy (Issue #3)**: The dev-log lists `base.py` as "Complete — imports all 12 models." This is misleading because none of the 12 model files contain actual class definitions. Update the dev-log to clearly mark all model files, route files, schema files, worker files, and test files as "Stub — placeholder for Phase X" so the next agent (or human) knows exactly what is and is not implemented.
4. **`session.py` exception handling (Issue #4)**: Add `as exc` to the `except Exception` clause and log before re-raising.
5. **`monitor_secret_key` default (Issue #5)**: Remove the `"change_me_in_production"` default or add a production validator.

The pattern of using `try/except ImportError` in `main.py` to lazily load phase-gated routers is excellent and exactly the right approach — it was just missing from `base.py`.

---

## What Must Be Fixed Before Phase 1 Can Begin

1. **DONE by Checker** — `src/backend/app/db/base.py`: import guards added. Developer must verify the fix does not conflict with their Phase 1 implementation approach.

2. **DONE by Checker** — `src/backend/.env.example`: AWS example credentials replaced with generic placeholders.

3. **Developer action required** — Update `docs/dev-log.md` to accurately report which files are fully implemented vs. stub-only. The current log implies all referenced files are complete when approximately 30 of the 50+ files listed are 1-line stubs. This creates a false picture of Phase 0 completion for any agent reading the log in Phase 1.

4. **Developer action required** — Before marking Task 0.5 (Alembic setup) as verified complete, run `alembic upgrade head` against the running PostgreSQL container and confirm it succeeds with the `base.py` fix in place. The empty baseline migration must apply cleanly.

5. **CEO action required** — Clarify free-tier positioning (Issue #10) in writing before Phase 5 (Stripe integration) begins. This does not block Phase 1–4 but must be resolved before Task 5.1 is started.

Once items 3 and 4 are confirmed complete, Phase 1 may proceed.
