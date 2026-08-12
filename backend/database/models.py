import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EMBEDDING_DIMENSIONS = 1536


class Base(DeclarativeBase):
    pass


class PolicyChunk(Base):
    """One semantically-chunked passage of a privacy policy, with its embedding."""

    __tablename__ = "policy_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    company: Mapped[str] = mapped_column(String(200), index=True)
    source: Mapped[str] = mapped_column(String(1000))
    section_heading: Mapped[str | None] = mapped_column(String(300), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PrivacyAttributes(Base):
    """Structured attributes extracted from one ingested policy (dashboard data)."""

    __tablename__ = "privacy_attributes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    company: Mapped[str] = mapped_column(String(200), index=True)
    source: Mapped[str] = mapped_column(String(1000))
    effective_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    data_collected: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    shares_with_third_parties: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    third_parties_named: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    sells_data: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    retention_period: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_rights: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    uses_cookies_tracking: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    children_data_collected: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    gdpr_mentioned: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    ccpa_mentioned: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    breach_notification: Mapped[str | None] = mapped_column(Text, nullable=True)
    international_transfer: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    risk_flags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChatLog(Base):
    """Every chat exchange. Backs the offline faithfulness-sampling and
    human-labeling hallucination-prevention layers (rag-design.md layers 5-6)."""

    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    retrieved_chunk_ids: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    top_similarity: Mapped[float | None] = mapped_column(Float, nullable=True)
    was_insufficient_context: Mapped[bool] = mapped_column(Boolean, default=False)
    human_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
