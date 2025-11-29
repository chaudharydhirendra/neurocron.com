"""
NeuroCron Campaign Model
Marketing campaigns and content management
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class CampaignStatus(str, enum.Enum):
    """Campaign lifecycle status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CampaignType(str, enum.Enum):
    """Types of marketing campaigns"""
    BRAND_AWARENESS = "brand_awareness"
    LEAD_GENERATION = "lead_generation"
    PRODUCT_LAUNCH = "product_launch"
    PROMOTION = "promotion"
    RETARGETING = "retargeting"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"


class ContentType(str, enum.Enum):
    """Types of content"""
    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    EMAIL = "email"
    AD_COPY = "ad_copy"
    LANDING_PAGE = "landing_page"
    VIDEO_SCRIPT = "video_script"
    PRESS_RELEASE = "press_release"


class Campaign(Base):
    """Marketing campaign model"""
    
    __tablename__ = "campaigns"
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Type and status
    campaign_type: Mapped[CampaignType] = mapped_column(
        SQLEnum(CampaignType),
        nullable=False,
    )
    status: Mapped[CampaignStatus] = mapped_column(
        SQLEnum(CampaignStatus),
        default=CampaignStatus.DRAFT,
        nullable=False,
    )
    
    # Scheduling
    start_date: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    
    # Budget
    budget: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    spent: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    
    # Targeting
    target_audience: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    channels: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(String),
        nullable=True,
    )
    
    # Goals & KPIs
    goals: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    
    # AI-generated strategy
    strategy: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    
    # Performance metrics
    metrics: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="campaigns",
    )
    contents: Mapped[List["CampaignContent"]] = relationship(
        "CampaignContent",
        back_populates="campaign",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Campaign {self.name}>"


class CampaignContent(Base):
    """Content items within a campaign"""
    
    __tablename__ = "campaign_contents"
    
    # Campaign reference
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Content info
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    content_type: Mapped[ContentType] = mapped_column(
        SQLEnum(ContentType),
        nullable=False,
    )
    body: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Status
    status: Mapped[str] = mapped_column(
        String(50),
        default="draft",
        nullable=False,
    )
    
    # Scheduling
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True,
    )
    
    # Channel & platform
    channel: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    platform: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    
    # AI metadata
    ai_generated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    ai_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    
    # Performance
    metrics: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
    )
    
    # Relationship
    campaign: Mapped["Campaign"] = relationship(
        "Campaign",
        back_populates="contents",
    )
    
    def __repr__(self) -> str:
        return f"<CampaignContent {self.title}>"

