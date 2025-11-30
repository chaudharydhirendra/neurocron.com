"""
NeuroCron Billing Models
Stripe subscription and payment management
"""

import uuid
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Subscription(Base):
    """Stripe subscription for an organization"""
    
    __tablename__ = "subscriptions"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Stripe IDs
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Plan info
    plan_name: Mapped[str] = mapped_column(String(50), default="free")  # free, starter, growth, enterprise
    plan_interval: Mapped[str] = mapped_column(String(20), default="month")  # month, year
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, past_due, canceled, trialing
    
    # Dates
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    current_period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Usage limits based on plan
    limits: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)


class Invoice(Base):
    """Billing invoice"""
    
    __tablename__ = "invoices"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Stripe ID
    stripe_invoice_id: Mapped[str] = mapped_column(String(255), unique=True)
    
    # Invoice details
    amount: Mapped[int] = mapped_column(Integer, default=0)  # Amount in cents
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, open, paid, void, uncollectible
    
    # URLs
    invoice_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    invoice_pdf: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Dates
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class UsageRecord(Base):
    """Track usage for metered billing"""
    
    __tablename__ = "usage_records"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Usage type
    metric: Mapped[str] = mapped_column(String(50), nullable=False)  # ai_tokens, emails_sent, campaigns_active
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    # Period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

