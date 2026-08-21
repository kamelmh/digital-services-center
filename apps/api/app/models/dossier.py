import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Dossier(Base):
    __tablename__ = "dossiers"
    __table_args__ = (Index("idx_dossiers_tenant", "tenant_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    beneficiary_name: Mapped[str | None] = mapped_column(String(255))
    wilaya: Mapped[str | None] = mapped_column(String(100))
    activity_type: Mapped[str | None] = mapped_column(String(100))
    total_cost: Mapped[int | None] = mapped_column(Integer)
    monthly_revenue: Mapped[int | None] = mapped_column(Integer)
    monthly_profit: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft|queued|ready|failed
    data_json: Mapped[dict | None] = mapped_column(JSON)
    content: Mapped[str | None] = mapped_column(Text)
    pdf_r2_key: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
