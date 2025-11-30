"""
NeuroCron CustomerDNA Models
Unified Customer Data Platform - aggregates all customer touchpoints
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CustomerProfile(Base):
    """
    Unified customer profile aggregating all touchpoints.
    Single source of truth for each customer.
    """
    
    __tablename__ = "customer_profiles"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Identity
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # CRM ID
    
    # Profile
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Demographics
    age_range: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    location_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timezone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Company (B2B)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Engagement metrics
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_page_views: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_email_opens: Mapped[int] = mapped_column(Integer, default=0)
    total_email_clicks: Mapped[int] = mapped_column(Integer, default=0)
    total_ad_impressions: Mapped[int] = mapped_column(Integer, default=0)
    total_ad_clicks: Mapped[int] = mapped_column(Integer, default=0)
    
    # Revenue metrics
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    average_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    lifetime_value: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Acquisition
    acquisition_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acquisition_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    acquisition_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Scores (0-100)
    engagement_score: Mapped[int] = mapped_column(Integer, default=50)
    purchase_likelihood: Mapped[int] = mapped_column(Integer, default=50)
    churn_risk: Mapped[int] = mapped_column(Integer, default=50)
    customer_fit_score: Mapped[int] = mapped_column(Integer, default=50)
    
    # Segments (JSON array of segment IDs)
    segments: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Tags (JSON array)
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Custom attributes (flexible JSON)
    custom_attributes: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Preferences
    email_opt_in: Mapped[bool] = mapped_column(Boolean, default=True)
    sms_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    push_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    first_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_purchase_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    events: Mapped[List["CustomerEvent"]] = relationship(
        "CustomerEvent",
        back_populates="customer",
        lazy="dynamic",
    )
    
    __table_args__ = (
        Index("ix_customer_profiles_org_email", "organization_id", "email"),
        Index("ix_customer_profiles_scores", "engagement_score", "churn_risk"),
    )


class CustomerEvent(Base):
    """
    Customer event/touchpoint tracking.
    Tracks all interactions across channels.
    """
    
    __tablename__ = "customer_events"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Organization (denormalized for query performance)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)  # page_view, click, purchase, email_open, etc.
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # website, email, ad, social, etc.
    channel: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # google, meta, email, etc.
    campaign_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Context
    page_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    referrer_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Device info
    device_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # desktop, mobile, tablet
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Location
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Value (for conversion events)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    
    # Additional properties (flexible JSON)
    properties: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    customer: Mapped["CustomerProfile"] = relationship("CustomerProfile", back_populates="events")
    
    __table_args__ = (
        Index("ix_customer_events_customer_time", "customer_id", "occurred_at"),
        Index("ix_customer_events_org_type", "organization_id", "event_type"),
    )


class CustomerSegment(Base):
    """
    Customer segment definition.
    Rules-based or AI-generated segments.
    """
    
    __tablename__ = "customer_segments"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Segment info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Type
    segment_type: Mapped[str] = mapped_column(String(50), default="manual")  # manual, rules, ai, dynamic
    
    # Rules (for rules-based segments)
    rules: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Stats
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    last_computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, default=False)  # Auto-updates membership


class CustomerJourney(Base):
    """
    Customer journey stage tracking.
    Maps customers through the marketing/sales funnel.
    """
    
    __tablename__ = "customer_journeys"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Journey stage
    current_stage: Mapped[str] = mapped_column(String(50), default="awareness")
    # Stages: awareness, consideration, evaluation, purchase, retention, advocacy
    
    # Stage timestamps
    awareness_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    consideration_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    evaluation_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    purchase_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retention_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    advocacy_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Journey health
    is_stalled: Mapped[bool] = mapped_column(Boolean, default=False)
    stalled_days: Mapped[int] = mapped_column(Integer, default=0)
    
    # Velocity (days to progress through stages)
    velocity_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100

