"""PipelineRun ORM model for AgroLens.

Records each execution of the daily imagery pipeline scheduler.
Provides an audit trail of how many fields were processed and
whether the run succeeded.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


PIPELINE_STATUS_ENUM = PgEnum(
    "running",
    "complete",
    "failed",
    name="pipelinestatus",
    create_type=False,
)


class PipelineRun(Base):
    """ORM model tracking a single daily pipeline scheduler execution.

    Attributes:
        id: UUID primary key.
        run_at: UTC timestamp when the run started.
        fields_processed: Number of fields successfully queued/processed.
        fields_failed: Number of fields that errored during processing.
        status: Outcome: running | complete | failed.
        error_message: Top-level error message if the run failed.
        created_at: Row creation timestamp (UTC).
    """

    __tablename__ = "pipeline_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Auto-generated UUID primary key.",
    )
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="UTC timestamp when the pipeline run started.",
    )
    fields_processed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Number of fields successfully queued/processed.",
    )
    fields_failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="Number of fields that encountered errors.",
    )
    status: Mapped[str] = mapped_column(
        PIPELINE_STATUS_ENUM,
        nullable=False,
        server_default="running",
        comment="Run status: running | complete | failed.",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Top-level error message if the run failed.",
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Row creation timestamp (UTC).",
    )
