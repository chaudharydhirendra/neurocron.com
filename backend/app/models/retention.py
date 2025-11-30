"""
NeuroCron RetentionAI Models
Churn prediction, retention automation, and loyalty programs
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class ChurnRiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChurnPrediction(Base):
    """
    Customer churn risk prediction.
    AI-generated risk scores with contributing factors.
    """
    
    __tablename__ = "churn_predictions"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    # Organization (denormalized)
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Risk assessment
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-100
    risk_level: Mapped[ChurnRiskLevel] = mapped_column(
        Enum(ChurnRiskLevel), default=ChurnRiskLevel.LOW
    )
    probability: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0-1.0
    
    # Contributing factors (JSON array)
    risk_factors: Mapped[dict] = mapped_column(JSONB, default=list)
    # Example: [{"factor": "inactivity", "weight": 0.4, "description": "No login in 30 days"}]
    
    # Signals used
    days_since_last_activity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    days_since_last_purchase: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    engagement_trend: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # declining, stable, increasing
    support_tickets_recent: Mapped[int] = mapped_column(Integer, default=0)
    negative_feedback_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Model info
    model_version: Mapped[str] = mapped_column(String(50), default="v1")
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_churn_predictions_org_score", "organization_id", "risk_score"),
    )


class RetentionCampaign(Base):
    """
    Automated retention campaign triggered by churn risk.
    """
    
    __tablename__ = "retention_campaigns"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campaign info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Trigger conditions
    trigger_risk_level: Mapped[ChurnRiskLevel] = mapped_column(
        Enum(ChurnRiskLevel), default=ChurnRiskLevel.HIGH
    )
    trigger_min_score: Mapped[int] = mapped_column(Integer, default=70)
    trigger_conditions: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Campaign type
    campaign_type: Mapped[str] = mapped_column(String(50), default="email")  # email, sms, push, multi
    
    # Content
    email_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sms_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    push_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    push_body: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Offer
    offer_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # discount, free_trial, upgrade
    offer_value: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    offer_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Stats
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    opened_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_count: Mapped[int] = mapped_column(Integer, default=0)
    converted_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_automated: Mapped[bool] = mapped_column(Boolean, default=True)


class RetentionAction(Base):
    """
    Individual retention action taken for a customer.
    """
    
    __tablename__ = "retention_actions"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Campaign (optional)
    campaign_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retention_campaigns.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)  # email_sent, sms_sent, offer_given
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Content sent
    content_subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_preview: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    offer_given: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Outcome tracking
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Result
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # retained, churned, pending
    
    # Timestamp
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LoyaltyProgram(Base):
    """
    Customer loyalty program configuration.
    """
    
    __tablename__ = "loyalty_programs"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Program info
    name: Mapped[str] = mapped_column(String(255), default="Rewards Program")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Points configuration
    points_name: Mapped[str] = mapped_column(String(50), default="Points")
    points_per_dollar: Mapped[float] = mapped_column(Float, default=1.0)
    points_per_referral: Mapped[int] = mapped_column(Integer, default=100)
    points_per_review: Mapped[int] = mapped_column(Integer, default=50)
    
    # Tiers (JSON array)
    tiers: Mapped[dict] = mapped_column(JSONB, default=list)
    # Example: [{"name": "Bronze", "min_points": 0}, {"name": "Silver", "min_points": 1000}]
    
    # Rewards (JSON array)
    rewards: Mapped[dict] = mapped_column(JSONB, default=list)
    # Example: [{"name": "$10 Off", "points_required": 500, "type": "discount"}]
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class CustomerLoyalty(Base):
    """
    Customer loyalty status and points.
    """
    
    __tablename__ = "customer_loyalty"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Program
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("loyalty_programs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Points
    total_points_earned: Mapped[int] = mapped_column(Integer, default=0)
    current_points: Mapped[int] = mapped_column(Integer, default=0)
    points_redeemed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Tier
    current_tier: Mapped[str] = mapped_column(String(50), default="Bronze")
    tier_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Activity
    last_earned_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_redeemed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Referrals
    referral_count: Mapped[int] = mapped_column(Integer, default=0)
    referral_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)


class LoyaltyTransaction(Base):
    """
    Loyalty points transaction log.
    """
    
    __tablename__ = "loyalty_transactions"
    
    # Customer loyalty
    customer_loyalty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_loyalty.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Transaction details
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # earn, redeem, expire, adjust
    points: Mapped[int] = mapped_column(Integer, nullable=False)  # positive for earn, negative for redeem
    
    # Source
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # purchase, referral, review, admin
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # order_id, etc.
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamp
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

