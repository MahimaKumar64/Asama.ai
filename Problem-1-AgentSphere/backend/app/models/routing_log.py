
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    String,
    Float,
    DateTime,
    ForeignKey,
    func,
    Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class RoutingLog(Base):
    __tablename__ = "routing_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    post_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE")
    )

    target_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE")
    )

    vector_score: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    hybrid_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    rerank_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    routing_decision: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    decision_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="NOTIFIED"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    feedback_applied: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false"
    )
