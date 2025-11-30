"""
NeuroCron API Router
Main router that includes all API endpoints
"""

from fastapi import APIRouter

from app.api.v1 import auth, organizations, campaigns, copilot, webhooks, dashboard, content, audit, integrations, flows, launchpad, personas, strategy, ads, channels, competitors, billing, websocket, notifications, teams, customer_dna, behavior, retention, viral, simulator, assets, projects, attribution, localization, agency

api_router = APIRouter()

# Authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Organization endpoints
api_router.include_router(
    organizations.router,
    prefix="/organizations",
    tags=["Organizations"]
)

# Campaign endpoints
api_router.include_router(
    campaigns.router,
    prefix="/campaigns",
    tags=["Campaigns"]
)

# NeuroCopilot AI endpoints
api_router.include_router(
    copilot.router,
    prefix="/copilot",
    tags=["NeuroCopilot"]
)

# Webhook endpoints
api_router.include_router(
    webhooks.router,
    prefix="/webhooks",
    tags=["Webhooks"]
)

# Dashboard endpoints
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

# ContentForge endpoints
api_router.include_router(
    content.router,
    prefix="/content",
    tags=["ContentForge"]
)

# AuditX endpoints
api_router.include_router(
    audit.router,
    prefix="/audit",
    tags=["AuditX"]
)

# Integrations endpoints
api_router.include_router(
    integrations.router,
    prefix="/integrations",
    tags=["Integrations"]
)

# FlowBuilder endpoints
api_router.include_router(
    flows.router,
    prefix="/flows",
    tags=["FlowBuilder"]
)

# LaunchPad endpoints
api_router.include_router(
    launchpad.router,
    prefix="/launchpad",
    tags=["LaunchPad"]
)

# AudienceGenome endpoints
api_router.include_router(
    personas.router,
    prefix="/personas",
    tags=["AudienceGenome"]
)

# NeuroPlan & BrainSpark endpoints
api_router.include_router(
    strategy.router,
    prefix="/strategy",
    tags=["NeuroPlan", "BrainSpark"]
)

# AdPilot endpoints
api_router.include_router(
    ads.router,
    prefix="/ads",
    tags=["AdPilot"]
)

# ChannelPulse endpoints
api_router.include_router(
    channels.router,
    prefix="/channels",
    tags=["ChannelPulse"]
)

# BattleStation, TrendRadar, CrisisShield endpoints
api_router.include_router(
    competitors.router,
    prefix="/intelligence",
    tags=["BattleStation", "TrendRadar", "CrisisShield"]
)

# Billing endpoints
api_router.include_router(
    billing.router,
    prefix="/billing",
    tags=["Billing"]
)

# WebSocket endpoints
api_router.include_router(
    websocket.router,
    prefix="/ws",
    tags=["WebSocket"]
)

# Notifications endpoints
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

# Team management endpoints
api_router.include_router(
    teams.router,
    prefix="/teams",
    tags=["Teams"]
)

# CustomerDNA endpoints
api_router.include_router(
    customer_dna.router,
    prefix="/customer-dna",
    tags=["CustomerDNA"]
)

# BehaviorMind endpoints
api_router.include_router(
    behavior.router,
    prefix="/behavior",
    tags=["BehaviorMind"]
)

# RetentionAI endpoints
api_router.include_router(
    retention.router,
    prefix="/retention",
    tags=["RetentionAI"]
)

# ViralEngine endpoints
api_router.include_router(
    viral.router,
    prefix="/viral",
    tags=["ViralEngine"]
)

# SimulatorX endpoints
api_router.include_router(
    simulator.router,
    prefix="/simulator",
    tags=["SimulatorX"]
)

# BrandVault endpoints
api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["BrandVault"]
)

# ProjectHub endpoints
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["ProjectHub"]
)

# RevenueLink endpoints
api_router.include_router(
    attribution.router,
    prefix="/attribution",
    tags=["RevenueLink"]
)

# GlobalReach endpoints
api_router.include_router(
    localization.router,
    prefix="/localization",
    tags=["GlobalReach"]
)

# ClientSync endpoints
api_router.include_router(
    agency.router,
    prefix="/agency",
    tags=["ClientSync"]
)

