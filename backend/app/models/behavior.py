"""
NeuroCron BehaviorMind Models
User behavior analytics, heatmaps, and session tracking
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PageSession(Base):
    """
    User page session tracking.
    Records detailed interaction data for behavior analysis.
    """
    
    __tablename__ = "page_sessions"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Visitor identification
    visitor_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Session info
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Page info
    page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    page_path: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    page_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    referrer_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Device info
    device_type: Mapped[str] = mapped_column(String(20), default="desktop")  # desktop, mobile, tablet
    browser: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    browser_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    os: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    screen_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    screen_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    viewport_width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    viewport_height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Location
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)
    
    # Engagement metrics
    scroll_depth_max: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    clicks_count: Mapped[int] = mapped_column(Integer, default=0)
    mouse_moves_count: Mapped[int] = mapped_column(Integer, default=0)
    keystrokes_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Flags
    is_bounce: Mapped[bool] = mapped_column(Boolean, default=True)
    had_rage_click: Mapped[bool] = mapped_column(Boolean, default=False)
    had_dead_click: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # UTM parameters
    utm_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    __table_args__ = (
        Index("ix_page_sessions_org_path", "organization_id", "page_path"),
        Index("ix_page_sessions_started", "organization_id", "started_at"),
    )


class ClickEvent(Base):
    """
    Click event tracking for heatmap generation.
    """
    
    __tablename__ = "click_events"
    
    # Session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("page_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Click position (relative to viewport)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Click position (relative to document)
    page_x: Mapped[int] = mapped_column(Integer, nullable=False)
    page_y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Element info
    element_tag: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    element_class: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    element_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    element_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    element_href: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Click type
    click_type: Mapped[str] = mapped_column(String(20), default="click")  # click, dblclick, contextmenu
    is_rage_click: Mapped[bool] = mapped_column(Boolean, default=False)
    is_dead_click: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScrollEvent(Base):
    """
    Scroll depth tracking.
    """
    
    __tablename__ = "scroll_events"
    
    # Session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("page_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Scroll position
    scroll_y: Mapped[int] = mapped_column(Integer, nullable=False)
    scroll_depth_percent: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    
    # Document height
    document_height: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FormInteraction(Base):
    """
    Form field interaction tracking.
    """
    
    __tablename__ = "form_interactions"
    
    # Session
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("page_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Form info
    form_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    form_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Field info
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)
    field_label: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Interaction
    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)  # focus, blur, change, input
    time_spent_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    # Field state
    was_filled: Mapped[bool] = mapped_column(Boolean, default=False)
    was_changed: Mapped[bool] = mapped_column(Boolean, default=False)
    was_cleared: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Hesitation/frustration indicators
    refill_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HeatmapSnapshot(Base):
    """
    Pre-computed heatmap data for performance.
    """
    
    __tablename__ = "heatmap_snapshots"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Page
    page_path: Mapped[str] = mapped_column(String(255), nullable=False)
    page_url: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Heatmap type
    heatmap_type: Mapped[str] = mapped_column(String(20), nullable=False)  # click, scroll, move
    device_type: Mapped[str] = mapped_column(String(20), default="desktop")
    
    # Data
    heatmap_data: Mapped[dict] = mapped_column(JSONB, default=dict)  # Pre-computed grid data
    
    # Stats
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    
    # Time range
    date_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_to: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Computed
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_heatmap_page_type", "organization_id", "page_path", "heatmap_type"),
    )


class ConversionFunnel(Base):
    """
    Conversion funnel definition and tracking.
    """
    
    __tablename__ = "conversion_funnels"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Funnel info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Steps (JSON array of step definitions)
    steps: Mapped[dict] = mapped_column(JSONB, default=list)
    # Each step: { "name": "Homepage", "type": "pageview", "pattern": "/", "order": 1 }
    
    # Stats (cached)
    total_entries: Mapped[int] = mapped_column(Integer, default=0)
    total_completions: Mapped[int] = mapped_column(Integer, default=0)
    conversion_rate: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_computed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

