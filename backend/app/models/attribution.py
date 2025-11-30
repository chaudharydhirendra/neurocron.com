"""
NeuroCron RevenueLink Models
Marketing-to-revenue attribution
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class AttributionModel(str, enum.Enum):
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    DATA_DRIVEN = "data_driven"


class RevenueEvent(Base):
    """
    Revenue event (sale, subscription, etc.)
    """
    
    __tablename__ = "revenue_events"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Customer
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Event details
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # purchase, subscription, renewal
    event_id: Mapped[str] = mapped_column(String(100), nullable=False)  # External order/transaction ID
    
    # Revenue
    revenue: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Product info
    product_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    product_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Source (from tracking)
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Attribution calculated
    attributed_campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    attribution_model: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    __table_args__ = (
        Index("ix_revenue_events_org_date", "organization_id", "occurred_at"),
    )


class TouchpointRecord(Base):
    """
    Marketing touchpoint in customer journey.
    """
    
    __tablename__ = "touchpoint_records"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Customer/Visitor
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    visitor_id: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Touchpoint info
    touchpoint_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: ad_click, organic_search, email_click, social_click, direct, referral
    
    # Channel
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Campaign
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    campaign_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Content/Creative
    content: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    keyword: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Page
    landing_page: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Timing
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Position in journey (set during attribution)
    journey_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_first_touch: Mapped[bool] = mapped_column(Boolean, default=False)
    is_last_touch: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (
        Index("ix_touchpoints_visitor", "visitor_id", "occurred_at"),
        Index("ix_touchpoints_customer", "customer_id", "occurred_at"),
    )


class AttributionResult(Base):
    """
    Calculated attribution for a revenue event.
    """
    
    __tablename__ = "attribution_results"
    
    # Revenue event
    revenue_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("revenue_events.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Touchpoint
    touchpoint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("touchpoint_records.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campaign
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Attribution
    attribution_model: Mapped[AttributionModel] = mapped_column(
        Enum(AttributionModel), nullable=False
    )
    
    # Credit
    credit_percentage: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    attributed_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Computed at
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ChannelPerformance(Base):
    """
    Aggregated channel performance metrics.
    """
    
    __tablename__ = "channel_performance"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Channel
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Metrics
    touchpoints: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    spend: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Calculated
    roas: Mapped[float] = mapped_column(Float, default=0.0)
    cpa: Mapped[float] = mapped_column(Float, default=0.0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Attribution model used
    attribution_model: Mapped[str] = mapped_column(String(50), default="last_touch")
    
    __table_args__ = (
        Index("ix_channel_perf_org_period", "organization_id", "period_start"),
    )


class CampaignROI(Base):
    """
    Campaign ROI tracking.
    """
    
    __tablename__ = "campaign_roi"
    
    # Campaign
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Spend
    total_spend: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Revenue by model
    revenue_first_touch: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_last_touch: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_linear: Mapped[float] = mapped_column(Float, default=0.0)
    revenue_data_driven: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Conversions
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Calculated ROI by model
    roi_first_touch: Mapped[float] = mapped_column(Float, default=0.0)
    roi_last_touch: Mapped[float] = mapped_column(Float, default=0.0)
    roi_linear: Mapped[float] = mapped_column(Float, default=0.0)
    roi_data_driven: Mapped[float] = mapped_column(Float, default=0.0)

