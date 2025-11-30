"""
NeuroCron API Router
Main router that includes all API endpoints
"""

from fastapi import APIRouter

from app.api.v1 import auth, organizations, campaigns, copilot, webhooks, dashboard, content, audit

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

