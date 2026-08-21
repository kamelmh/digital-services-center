import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (Index("idx_jobs_tenant", "tenant_id"), Index("idx_jobs_status", "status"))

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    dossier_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("dossiers.id", ondelete="SET NULL"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # feasibility|business_plan|nesda|orchestration
    status: Mapped[str] = mapped_column(String(20), default="queued")  # queued|running|done|failed
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    provider: Mapped[str | None] = mapped_column(String(50))  # groq|openrouter|offline
    result: Mapped[dict | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
