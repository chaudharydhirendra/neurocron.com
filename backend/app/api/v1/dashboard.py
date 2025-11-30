"""
NeuroCron Dashboard API
Aggregated stats and insights
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.campaign import Campaign, CampaignStatus
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

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

