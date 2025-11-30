"""
NeuroCron ClientSync Models
Agency white-label mode
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AgencyClient(Base):
    """
    Agency's client organization.
    """
    
    __tablename__ = "agency_clients"
    
    # Agency (parent organization)
    agency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Client (child organization)
    client_organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Client info (for agency view)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Contact
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Contract
    contract_start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    contract_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    monthly_retainer: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active")  # active, paused, churned
    
    # Notes
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Permissions
    can_access_billing: Mapped[bool] = mapped_column(Boolean, default=False)
    can_access_analytics: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index("ix_agency_clients_agency", "agency_id"),
    )


class WhiteLabelConfig(Base):
    """
    White-label branding configuration.
    """
    
    __tablename__ = "white_label_configs"
    
    # Organization (agency or client)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Branding
    brand_name: Mapped[str] = mapped_column(String(255), default="NeuroCron")
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo_dark_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Colors
    primary_color: Mapped[str] = mapped_column(String(20), default="#0066FF")
    secondary_color: Mapped[str] = mapped_column(String(20), default="#8B5CF6")
    accent_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Domain
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Email
    email_from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_from_address: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Features to hide
    hidden_features: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Custom CSS
    custom_css: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Footer
    footer_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    hide_powered_by: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)


class ClientReport(Base):
    """
    Automated client reports.
    """
    
    __tablename__ = "client_reports"
    
    # Agency client
    agency_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agency_clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Report info
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), default="monthly")  # weekly, monthly, quarterly
    
    # Period
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Content
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    highlights: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # File
    file_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_format: Mapped[str] = mapped_column(String(10), default="pdf")  # pdf, pptx, xlsx
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, pending_review, sent
    
    # Delivery
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class ClientApproval(Base):
    """
    Client approval workflow.
    """
    
    __tablename__ = "client_approvals"
    
    # Agency client
    agency_client_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agency_clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Item to approve
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # campaign, content, creative
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    item_title: Mapped[str] = mapped_column(String(255), nullable=False)
    item_preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Request
    requested_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Response
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, rejected, revision_requested
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    response_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    __table_args__ = (
        Index("ix_client_approvals_status", "agency_client_id", "status"),
    )

