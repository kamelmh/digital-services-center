import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Checkout(Base):
    __tablename__ = "checkouts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan: Mapped[str] = mapped_column(String(20), nullable=False)  # starter|pro|business
    billing_cycle: Mapped[str] = mapped_column(String(20), default="monthly")
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # DZD
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending|paid|failed
    gateway: Mapped[str] = mapped_column(String(20), default="mock")
    gateway_checkout_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
