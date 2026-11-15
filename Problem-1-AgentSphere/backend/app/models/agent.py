import uuid
from datetime import datetime

from sqlalchemy import (
    String, Text, Float, DateTime,
    func, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    company_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    industry_category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    webhook_url: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    interest_manifesto: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    interest_embedding: Mapped[list | None] = mapped_column(
        Vector(1536), nullable=True
    )

    trust_score: Mapped[float] = mapped_column(
        Float, default=1.0
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    blocked_domains: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    blocked_industries: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
