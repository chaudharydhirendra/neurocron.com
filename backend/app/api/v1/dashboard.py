"""
NeuroCron Dashboard API
Aggregated stats, insights, and real-time analytics
"""

from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import List, Optional

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.campaign import Campaign, CampaignStatus
from app.models.organization import Organization, OrganizationMember
from app.models.user import User
from app.models.persona import Persona
from app.models.flow import Flow
from app.models.integration import IntegrationToken, IntegrationStatus
from app.models.billing import UsageRecord

router = APIRouter()


class DashboardStats(BaseModel):
    total_campaigns: int
    active_campaigns: int
    paused_campaigns: int
    draft_campaigns: int
    total_budget: float
    active_budget: float


class RecentCampaign(BaseModel):
    id: str
    name: str
    status: str
    budget: float | None
    created_at: str


class DashboardResponse(BaseModel):
    stats: DashboardStats
    recent_campaigns: List[RecentCampaign]
    organization_name: str


@router.get("/", response_model=DashboardResponse)
async def get_dashboard(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard stats and recent activity.
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.is_active == True)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    # Get organization
    org_result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = org_result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get campaign counts by status
    total_result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.organization_id == org_id)
    )
    total_campaigns = total_result.scalar() or 0
    
    active_result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.organization_id == org_id)
        .where(Campaign.status == CampaignStatus.ACTIVE)
    )
    active_campaigns = active_result.scalar() or 0
    
    paused_result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.organization_id == org_id)
        .where(Campaign.status == CampaignStatus.PAUSED)
    )
    paused_campaigns = paused_result.scalar() or 0
    
    draft_result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.organization_id == org_id)
        .where(Campaign.status == CampaignStatus.DRAFT)
    )
    draft_campaigns = draft_result.scalar() or 0
    
    # Get total budget
    total_budget_result = await db.execute(
        select(func.coalesce(func.sum(Campaign.budget), 0))
        .where(Campaign.organization_id == org_id)
    )
    total_budget = float(total_budget_result.scalar() or 0)
    
    # Get active budget
    active_budget_result = await db.execute(
        select(func.coalesce(func.sum(Campaign.budget), 0))
        .where(Campaign.organization_id == org_id)
        .where(Campaign.status == CampaignStatus.ACTIVE)
    )
    active_budget = float(active_budget_result.scalar() or 0)
    
    # Get recent campaigns
    recent_result = await db.execute(
        select(Campaign)
        .where(Campaign.organization_id == org_id)
        .order_by(Campaign.created_at.desc())
        .limit(5)
    )
    recent_campaigns_db = recent_result.scalars().all()
    
    recent_campaigns = [
        RecentCampaign(
            id=str(c.id),
            name=c.name,
            status=c.status.value,
            budget=float(c.budget) if c.budget else None,
            created_at=c.created_at.isoformat() if c.created_at else ""
        )
        for c in recent_campaigns_db
    ]
    
    return DashboardResponse(
        stats=DashboardStats(
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            paused_campaigns=paused_campaigns,
            draft_campaigns=draft_campaigns,
            total_budget=total_budget,
            active_budget=active_budget,
        ),
        recent_campaigns=recent_campaigns,
        organization_name=org.name,
    )


@router.get("/overview")
async def get_overview(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard overview with all key metrics.
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    # Campaign stats
    campaign_result = await db.execute(
        select(
            func.count(Campaign.id).label("total"),
            func.sum(func.case((Campaign.status == CampaignStatus.ACTIVE, 1), else_=0)).label("active"),
            func.sum(func.coalesce(Campaign.budget, 0)).label("total_budget"),
        )
        .where(Campaign.organization_id == org_id)
    )
    campaign_stats = campaign_result.one()
    
    # Persona count
    persona_result = await db.execute(
        select(func.count(Persona.id))
        .where(Persona.organization_id == org_id)
    )
    persona_count = persona_result.scalar() or 0
    
    # Flow count
    flow_result = await db.execute(
        select(func.count(Flow.id))
        .where(Flow.organization_id == org_id)
    )
    flow_count = flow_result.scalar() or 0
    
    # Integration count
    integration_result = await db.execute(
        select(func.count(IntegrationToken.id))
        .where(IntegrationToken.organization_id == org_id)
        .where(IntegrationToken.status == IntegrationStatus.CONNECTED)
    )
    integration_count = integration_result.scalar() or 0
    
    # AI usage this month
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage_result = await db.execute(
        select(func.coalesce(func.sum(UsageRecord.quantity), 0))
        .where(UsageRecord.organization_id == org_id)
        .where(UsageRecord.metric_type == "ai_tokens")
        .where(UsageRecord.created_at >= month_start)
    )
    ai_tokens_used = usage_result.scalar() or 0
    
    return {
        "campaigns": {
            "total": int(campaign_stats.total or 0),
            "active": int(campaign_stats.active or 0),
            "total_budget": float(campaign_stats.total_budget or 0),
        },
        "personas": persona_count,
        "flows": flow_count,
        "integrations": integration_count,
        "ai_usage": {
            "tokens_used": int(ai_tokens_used),
            "period": month_start.strftime("%B %Y"),
        },
        "health_score": _calculate_health_score(
            int(campaign_stats.active or 0),
            integration_count,
            persona_count,
            flow_count,
        ),
    }


def _calculate_health_score(
    active_campaigns: int,
    integrations: int,
    personas: int,
    flows: int,
) -> dict:
    """Calculate platform health score based on setup completeness."""
    score = 0
    max_score = 100
    
    # Weight factors
    if active_campaigns >= 1:
        score += 20
    if active_campaigns >= 3:
        score += 10
    
    if integrations >= 1:
        score += 20
    if integrations >= 3:
        score += 10
    
    if personas >= 1:
        score += 15
    if personas >= 3:
        score += 5
    
    if flows >= 1:
        score += 15
    if flows >= 3:
        score += 5
    
    return {
        "score": min(score, max_score),
        "status": "excellent" if score >= 80 else "good" if score >= 50 else "needs_setup",
        "recommendations": _get_recommendations(active_campaigns, integrations, personas, flows),
    }


def _get_recommendations(campaigns: int, integrations: int, personas: int, flows: int) -> List[str]:
    """Get setup recommendations."""
    recs = []
    
    if integrations == 0:
        recs.append("Connect your first marketing platform in Settings → Integrations")
    
    if personas == 0:
        recs.append("Generate customer personas in Audiences to improve targeting")
    
    if campaigns == 0:
        recs.append("Create your first campaign to start marketing")
    
    if flows == 0:
        recs.append("Build an automation flow to engage customers automatically")
    
    if not recs:
        recs.append("Great job! Your marketing engine is well configured.")
    
    return recs[:3]


@router.get("/activity")
async def get_activity(
    org_id: UUID = Query(..., description="Organization ID"),
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get recent activity timeline.
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get recent campaigns
    campaign_result = await db.execute(
        select(Campaign)
        .where(Campaign.organization_id == org_id)
        .where(Campaign.created_at >= since)
        .order_by(Campaign.created_at.desc())
        .limit(10)
    )
    campaigns = campaign_result.scalars().all()
    
    # Get recent personas
    persona_result = await db.execute(
        select(Persona)
        .where(Persona.organization_id == org_id)
        .where(Persona.created_at >= since)
        .order_by(Persona.created_at.desc())
        .limit(5)
    )
    personas = persona_result.scalars().all()
    
    # Build activity timeline
    activities = []
    
    for c in campaigns:
        activities.append({
            "type": "campaign_created",
            "title": f"Campaign created: {c.name}",
            "timestamp": c.created_at.isoformat() if c.created_at else None,
            "icon": "megaphone",
        })
    
    for p in personas:
        activities.append({
            "type": "persona_created",
            "title": f"Persona generated: {p.name}",
            "timestamp": p.created_at.isoformat() if p.created_at else None,
            "icon": "user",
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"] or "", reverse=True)
    
    return {"activities": activities[:15], "period_days": days}


@router.get("/quick-actions")
async def get_quick_actions(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get contextual quick actions based on platform state.
    """
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    actions = []
    
    # Check integrations
    int_result = await db.execute(
        select(func.count(IntegrationToken.id))
        .where(IntegrationToken.organization_id == org_id)
        .where(IntegrationToken.status == IntegrationStatus.CONNECTED)
    )
    if (int_result.scalar() or 0) == 0:
        actions.append({
            "id": "connect_platform",
            "title": "Connect Marketing Platform",
            "description": "Link Google, Meta, or LinkedIn to sync your data",
            "url": "/settings?tab=integrations",
            "priority": "high",
            "icon": "link",
        })
    
    # Check personas
    persona_result = await db.execute(
        select(func.count(Persona.id)).where(Persona.organization_id == org_id)
    )
    if (persona_result.scalar() or 0) == 0:
        actions.append({
            "id": "create_persona",
            "title": "Generate Customer Personas",
            "description": "AI will create detailed buyer personas for targeting",
            "url": "/audiences",
            "priority": "high",
            "icon": "users",
        })
    
    # Check campaigns
    campaign_result = await db.execute(
        select(func.count(Campaign.id)).where(Campaign.organization_id == org_id)
    )
    if (campaign_result.scalar() or 0) == 0:
        actions.append({
            "id": "create_campaign",
            "title": "Create First Campaign",
            "description": "Launch your first marketing campaign",
            "url": "/dashboard/campaigns/new",
            "priority": "medium",
            "icon": "rocket",
        })
    
    # Always offer these
    actions.extend([
        {
            "id": "generate_strategy",
            "title": "Generate Marketing Strategy",
            "description": "Get an AI-powered 12-month marketing roadmap",
            "url": "/strategy",
            "priority": "medium",
            "icon": "brain",
        },
        {
            "id": "create_content",
            "title": "Generate Content",
            "description": "Create blog posts, social content, or ads",
            "url": "/content",
            "priority": "low",
            "icon": "edit",
        },
    ])
    
    return {"actions": actions[:5]}

