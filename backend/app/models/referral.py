"""
NeuroCron ViralEngine Models
Referral programs, gamification, contests, and viral marketing
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class ReferralProgramStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class ReferralProgram(Base):
    """
    Referral program configuration.
    """
    
    __tablename__ = "referral_programs"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Program info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Reward for referrer
    referrer_reward_type: Mapped[str] = mapped_column(String(50), default="credit")  # credit, discount, points, custom
    referrer_reward_value: Mapped[float] = mapped_column(Float, default=10.0)
    referrer_reward_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Reward for referred (new customer)
    referred_reward_type: Mapped[str] = mapped_column(String(50), default="discount")
    referred_reward_value: Mapped[float] = mapped_column(Float, default=10.0)
    referred_reward_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Conditions
    min_purchase_amount: Mapped[float] = mapped_column(Float, default=0.0)
    max_referrals_per_user: Mapped[int] = mapped_column(Integer, default=0)  # 0 = unlimited
    reward_on_event: Mapped[str] = mapped_column(String(50), default="signup")  # signup, first_purchase, subscription
    
    # Expiry
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Stats
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)
    successful_referrals: Mapped[int] = mapped_column(Integer, default=0)
    total_rewards_given: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Status
    status: Mapped[ReferralProgramStatus] = mapped_column(
        Enum(ReferralProgramStatus), default=ReferralProgramStatus.DRAFT
    )


class Referral(Base):
    """
    Individual referral tracking.
    """
    
    __tablename__ = "referrals"
    
    # Program
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("referral_programs.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Referrer (existing customer)
    referrer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Referred (new customer)
    referred_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Referral info
    referral_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    referral_link: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Contact info (before conversion)
    referred_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    referred_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, clicked, signed_up, converted, rewarded
    
    # Tracking
    click_count: Mapped[int] = mapped_column(Integer, default=0)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    signed_up_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    converted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Rewards
    referrer_rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    referred_rewarded: Mapped[bool] = mapped_column(Boolean, default=False)
    referrer_reward_amount: Mapped[float] = mapped_column(Float, default=0.0)
    referred_reward_amount: Mapped[float] = mapped_column(Float, default=0.0)
    
    __table_args__ = (
        Index("ix_referrals_referrer", "referrer_id"),
        Index("ix_referrals_code", "referral_code"),
    )


class Contest(Base):
    """
    Marketing contest/giveaway.
    """
    
    __tablename__ = "contests"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Contest info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Prize
    prize_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prize_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prize_value: Mapped[float] = mapped_column(Float, default=0.0)
    prize_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Entry methods (JSON array)
    entry_methods: Mapped[dict] = mapped_column(JSONB, default=list)
    # Example: [{"type": "signup", "points": 10}, {"type": "share_twitter", "points": 5}]
    
    # Winners
    winner_count: Mapped[int] = mapped_column(Integer, default=1)
    winner_selection: Mapped[str] = mapped_column(String(50), default="random")  # random, top_points
    
    # Timing
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Stats
    total_entries: Mapped[int] = mapped_column(Integer, default=0)
    unique_participants: Mapped[int] = mapped_column(Integer, default=0)
    total_shares: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, active, ended, winners_selected
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)


class ContestEntry(Base):
    """
    Contest entry/participation.
    """
    
    __tablename__ = "contest_entries"
    
    # Contest
    contest_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contests.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Participant
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Entry info
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Points
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    
    # Actions completed (JSON)
    actions_completed: Mapped[dict] = mapped_column(JSONB, default=list)
    
    # Winner status
    is_winner: Mapped[bool] = mapped_column(Boolean, default=False)
    winner_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    __table_args__ = (
        Index("ix_contest_entries_contest_email", "contest_id", "email", unique=True),
    )


class GamificationBadge(Base):
    """
    Achievement badges for gamification.
    """
    
    __tablename__ = "gamification_badges"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Badge info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Criteria
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)  # referrals, purchases, engagement, custom
    criteria_value: Mapped[int] = mapped_column(Integer, default=1)  # e.g., 5 referrals
    criteria_rules: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Reward
    points_reward: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)


class CustomerBadge(Base):
    """
    Badges earned by customers.
    """
    
    __tablename__ = "customer_badges"
    
    # Customer
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customer_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Badge
    badge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gamification_badges.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Earned
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_customer_badges_unique", "customer_id", "badge_id", unique=True),
    )


class Leaderboard(Base):
    """
    Leaderboard configuration.
    """
    
    __tablename__ = "leaderboards"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Leaderboard info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Type
    metric: Mapped[str] = mapped_column(String(50), nullable=False)  # referrals, purchases, points, custom
    
    # Time period
    period: Mapped[str] = mapped_column(String(20), default="all_time")  # daily, weekly, monthly, all_time
    
    # Display
    show_top: Mapped[int] = mapped_column(Integer, default=10)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

