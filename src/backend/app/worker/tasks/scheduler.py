"""Celery task: daily imagery pipeline trigger.

Queries all fields that have no vegetation index composite more recent
than 10 days and enqueues fetch + compute tasks for each.  Records
the pipeline run outcome in the ``pipeline_runs`` table.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from app.worker.celery_app import celery_app

logger = logging.getLogger(__name__)

_STALE_DAYS = 10


@celery_app.task(name="scheduler.trigger_daily_imagery_pipeline")
def trigger_daily_imagery_pipeline() -> dict[str, int]:
    """Enqueue imagery fetch + index tasks for all fields with stale data.

    A field is considered stale when its most recent ``VegetationIndex``
    record has a ``composite_end`` date older than :data:`_STALE_DAYS` days,
    or when it has no composites at all.

    Returns:
        Dict with ``fields_enqueued`` and ``fields_skipped`` counts.
    """
    import uuid
    from datetime import date

    from sqlalchemy import func, select, text

    from app.db.session import SessionLocal
    from app.models.field import Field
    from app.models.pipeline_run import PipelineRun
    from app.models.vegetation_index import VegetationIndex
    from app.worker.tasks.imagery import fetch_field_imagery
    from app.worker.tasks.indices import compute_field_indices

    run_at = datetime.now(tz=timezone.utc)
    cutoff = (run_at - timedelta(days=_STALE_DAYS)).date()

    # Record start of pipeline run
    with SessionLocal() as db:
        pipeline_run = PipelineRun(run_at=run_at, status="running")
        db.add(pipeline_run)
        db.commit()
        db.refresh(pipeline_run)
        run_id = pipeline_run.id

    enqueued = 0
    failed = 0

    try:
        with SessionLocal() as db:
            # Find fields with no composites or whose latest composite is stale
            latest_composite = (
                select(
                    VegetationIndex.field_id,
                    func.max(VegetationIndex.composite_end).label("latest_end"),
                )
                .where(VegetationIndex.index_type == "ndvi")
                .group_by(VegetationIndex.field_id)
                .subquery()
            )

            # All fields that are either missing from the subquery or stale
            stale_fields = db.execute(
                select(Field.id).outerjoin(
                    latest_composite,
                    Field.id == latest_composite.c.field_id,
                ).where(
                    (latest_composite.c.latest_end == None)  # noqa: E711
                    | (latest_composite.c.latest_end < cutoff)
                )
            ).scalars().all()

        composite_start = str(cutoff - timedelta(days=_STALE_DAYS))
        composite_end = str(run_at.date())

        for field_id in stale_fields:
            try:
                # Chain: fetch imagery → then compute indices
                (
                    fetch_field_imagery.s(str(field_id))
                    | compute_field_indices.s(composite_start, composite_end)
                ).apply_async()
                enqueued += 1
                logger.info(
                    "trigger_daily_imagery_pipeline: enqueued pipeline for field=%s",
                    field_id,
                )
            except Exception as exc:
                logger.error(
                    "trigger_daily_imagery_pipeline: failed to enqueue field=%s: %s",
                    field_id, exc,
                )
                failed += 1

        with SessionLocal() as db:
            run = db.get(PipelineRun, run_id)
            if run:
                run.status = "complete"
                run.fields_processed = enqueued
                run.fields_failed = failed
                db.commit()

    except Exception as exc:
        logger.error("trigger_daily_imagery_pipeline: fatal error: %s", exc)
        with SessionLocal() as db:
            run = db.get(PipelineRun, run_id)
            if run:
                run.status = "failed"
                run.error_message = str(exc)
                db.commit()
        raise

    logger.info(
        "trigger_daily_imagery_pipeline: enqueued=%d failed=%d", enqueued, failed
    )
    return {"fields_enqueued": enqueued, "fields_skipped": failed}
