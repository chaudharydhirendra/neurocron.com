"""
NeuroCron Ad Models
AdPilot campaigns and ad variants
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class AdCampaign(Base):
    """Ad campaign managed by AdPilot"""
    
    __tablename__ = "ad_campaigns"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campaign basics
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # google, meta, linkedin, tiktok
    campaign_type: Mapped[str] = mapped_column(String(50), default="conversion")  # awareness, consideration, conversion
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, paused, ended
    
    # Budget
    budget: Mapped[float] = mapped_column(Float, default=0.0)
    budget_type: Mapped[str] = mapped_column(String(20), default="daily")  # daily, lifetime
    spent: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Targeting
    targeting: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Schedule
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Performance metrics
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    ctr: Mapped[float] = mapped_column(Float, default=0.0)
    cpc: Mapped[float] = mapped_column(Float, default=0.0)
    cpa: Mapped[float] = mapped_column(Float, default=0.0)
    roas: Mapped[float] = mapped_column(Float, default=0.0)
    
    # External IDs
    external_campaign_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationships
    variants: Mapped[List["AdVariant"]] = relationship(
        "AdVariant",
        back_populates="campaign",
        lazy="dynamic",
    )


class AdVariant(Base):
    """Ad creative variant"""
    
    __tablename__ = "ad_variants"
    
    # Campaign
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Creative content
    headline: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cta: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # AI predictions
    predicted_ctr: Mapped[float] = mapped_column(Float, default=0.0)
    predicted_conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Actual performance
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, paused
    is_winner: Mapped[bool] = mapped_column(default=False)
    
    # Relationships
    campaign: Mapped["AdCampaign"] = relationship("AdCampaign", back_populates="variants")


class AdOptimizationSuggestion(Base):
    """AI-generated optimization suggestion"""
    
    __tablename__ = "ad_optimization_suggestions"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campaign reference
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ad_campaigns.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Suggestion details
    suggestion_type: Mapped[str] = mapped_column(String(50), nullable=False)  # budget, targeting, creative, bid
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # high, medium, low
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_impact: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Action to take
    action: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, applied, dismissed

