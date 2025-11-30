"""
NeuroCron Intelligence Models
BattleStation, TrendRadar, and CrisisShield
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Competitor(Base):
    """Tracked competitor for BattleStation"""
    
    __tablename__ = "competitors"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Analysis
    health_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    threat_level: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    
    # Metrics
    website_traffic: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    social_followers: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    domain_authority: Mapped[int] = mapped_column(Integer, default=0)
    ad_spend_estimate: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Additional metrics as JSON
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    last_analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    insights: Mapped[List["CompetitorInsight"]] = relationship(
        "CompetitorInsight",
        back_populates="competitor",
        lazy="dynamic",
    )


class CompetitorInsight(Base):
    """Intelligence insight about a competitor"""
    
    __tablename__ = "competitor_insights"
    
    # Competitor
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("competitors.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Insight details
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # new_product, pricing_change, campaign, content, social
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Impact assessment
    impact: Mapped[str] = mapped_column(String(20), default="neutral")  # positive, neutral, negative
    action_recommended: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Status
    is_read: Mapped[bool] = mapped_column(default=False)
    is_actioned: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    competitor: Mapped["Competitor"] = relationship("Competitor", back_populates="insights")


class Trend(Base):
    """Trending topic tracked by TrendRadar"""
    
    __tablename__ = "trends"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Trend info
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # technology, industry, compliance, tactics
    
    # Velocity
    velocity: Mapped[str] = mapped_column(String(20), default="stable")  # viral, rising, stable, declining
    growth_24h: Mapped[int] = mapped_column(Integer, default=0)
    volume: Mapped[int] = mapped_column(Integer, default=0)
    
    # Analysis
    sentiment: Mapped[str] = mapped_column(String(20), default="neutral")
    relevance_score: Mapped[int] = mapped_column(Integer, default=50)  # 0-100
    
    # Source breakdown
    source_breakdown: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Opportunity
    opportunity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Time tracking
    first_detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BrandMention(Base):
    """Brand mention for CrisisShield"""
    
    __tablename__ = "brand_mentions"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Source
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # twitter, linkedin, reddit, news, review
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Author
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_handle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Analysis
    sentiment: Mapped[str] = mapped_column(String(20), default="neutral")
    reach: Mapped[int] = mapped_column(Integer, default=0)
    engagement: Mapped[int] = mapped_column(Integer, default=0)
    
    # Action
    requires_action: Mapped[bool] = mapped_column(default=False)
    is_responded: Mapped[bool] = mapped_column(default=False)
    response_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class CrisisEvent(Base):
    """Brand crisis event"""
    
    __tablename__ = "crisis_events"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Crisis details
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="low")  # critical, high, medium, low
    
    # Metrics
    mentions_count: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_trend: Mapped[str] = mapped_column(String(20), default="stable")  # improving, stable, declining
    
    # Actions
    recommended_actions: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Resolution
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, monitoring, resolved
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

