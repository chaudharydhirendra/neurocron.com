"""
NeuroCron Database Models
SQLAlchemy ORM models for all entities
"""

from app.models.base import Base
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.models.campaign import Campaign, CampaignContent
from app.models.flow import Flow, FlowExecution
from app.models.persona import Persona, AudienceSegment
from app.models.strategy import MarketingStrategy, CreativeIdea
from app.models.ad import AdCampaign, AdVariant, AdOptimizationSuggestion
from app.models.social import SocialAccount, ScheduledPost, InboxMessage
from app.models.intelligence import (
    Competitor,
    CompetitorInsight,
    Trend,
    BrandMention,
    CrisisEvent,
)
from app.models.billing import Subscription, Invoice, UsageRecord

__all__ = [
    "Base",
    # Users & Organizations
    "User",
    "Organization",
    "OrganizationMember",
    # Campaigns
    "Campaign",
    "CampaignContent",
    # FlowBuilder
    "Flow",
    "FlowExecution",
    # AudienceGenome
    "Persona",
    "AudienceSegment",
    # NeuroPlan & BrainSpark
    "MarketingStrategy",
    "CreativeIdea",
    # AdPilot
    "AdCampaign",
    "AdVariant",
    "AdOptimizationSuggestion",
    # ChannelPulse
    "SocialAccount",
    "ScheduledPost",
    "InboxMessage",
    # Intelligence (BattleStation, TrendRadar, CrisisShield)
    "Competitor",
    "CompetitorInsight",
    "Trend",
    "BrandMention",
    "CrisisEvent",
    # Billing
    "Subscription",
    "Invoice",
    "UsageRecord",
]
