"""
NeuroCron Social Models
ChannelPulse social media management
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class SocialAccount(Base):
    """Connected social media account"""
    
    __tablename__ = "social_accounts"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Platform info
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # facebook, instagram, twitter, linkedin
    account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # OAuth tokens (encrypted in production)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Stats
    followers: Mapped[int] = mapped_column(Integer, default=0)
    following: Mapped[int] = mapped_column(Integer, default=0)
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    is_connected: Mapped[bool] = mapped_column(default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ScheduledPost(Base):
    """Scheduled social media post"""
    
    __tablename__ = "scheduled_posts"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Channels (JSON array of platform names)
    channels: Mapped[dict] = mapped_column(JSONB, default=list)
    
    # Media
    media_urls: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Schedule
    scheduled_for: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled, published, failed, cancelled
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Performance (after publishing)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    engagements: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)


class InboxMessage(Base):
    """Unified inbox message from any channel"""
    
    __tablename__ = "inbox_messages"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Source
    channel: Mapped[str] = mapped_column(String(50), nullable=False)  # facebook, instagram, twitter, linkedin, email
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)  # comment, message, mention, review
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Author
    author_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_handle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # AI analysis
    sentiment: Mapped[str] = mapped_column(String(20), default="neutral")  # positive, neutral, negative
    priority: Mapped[str] = mapped_column(String(20), default="low")  # high, medium, low
    
    # Status
    is_read: Mapped[bool] = mapped_column(default=False)
    is_replied: Mapped[bool] = mapped_column(default=False)
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reply_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Original post reference
    post_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

