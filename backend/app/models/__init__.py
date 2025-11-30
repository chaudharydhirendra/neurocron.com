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
from app.models.notification import Notification
from app.models.customer import CustomerProfile, CustomerEvent, CustomerSegment, CustomerJourney
from app.models.behavior import PageSession, ClickEvent, ScrollEvent, FormInteraction, HeatmapSnapshot, ConversionFunnel
from app.models.retention import ChurnPrediction, ChurnRiskLevel, RetentionCampaign, RetentionAction, LoyaltyProgram, CustomerLoyalty, LoyaltyTransaction
from app.models.referral import ReferralProgram, ReferralProgramStatus, Referral, Contest, ContestEntry, GamificationBadge, CustomerBadge, Leaderboard
from app.models.simulation import Simulation, SimulationStatus, SimulationType, SimulationTemplate, PredictionModel, ForecastScenario
from app.models.asset import Asset, AssetType, AssetFolder, AssetTag, AssetTagMapping, BrandGuideline

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
    # Notifications
    "Notification",
    # CustomerDNA
    "CustomerProfile",
    "CustomerEvent",
    "CustomerSegment",
    "CustomerJourney",
    # BehaviorMind
    "PageSession",
    "ClickEvent",
    "ScrollEvent",
    "FormInteraction",
    "HeatmapSnapshot",
    "ConversionFunnel",
    # RetentionAI
    "ChurnPrediction",
    "ChurnRiskLevel",
    "RetentionCampaign",
    "RetentionAction",
    "LoyaltyProgram",
    "CustomerLoyalty",
    "LoyaltyTransaction",
    # ViralEngine
    "ReferralProgram",
    "ReferralProgramStatus",
    "Referral",
    "Contest",
    "ContestEntry",
    "GamificationBadge",
    "CustomerBadge",
    "Leaderboard",
    # SimulatorX
    "Simulation",
    "SimulationStatus",
    "SimulationType",
    "SimulationTemplate",
    "PredictionModel",
    "ForecastScenario",
    # BrandVault
    "Asset",
    "AssetType",
    "AssetFolder",
    "AssetTag",
    "AssetTagMapping",
    "BrandGuideline",
]
