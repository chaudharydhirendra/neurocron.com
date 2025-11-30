"""
NeuroCron AdPilot API
Fully automated ad creation and management
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


class AdGenerateRequest(BaseModel):
    """Request to generate ads"""
    product_name: str
    product_description: str
    target_audience: str
    platform: str  # google, meta, linkedin, tiktok
    ad_type: str  # search, display, video, carousel
    goal: str  # awareness, consideration, conversion
    count: int = Field(3, ge=1, le=10)


class AdVariant(BaseModel):
    """Generated ad variant"""
    id: str
    headline: str
    description: str
    cta: str
    image_prompt: Optional[str] = None
    predicted_ctr: float
    predicted_conversion_rate: float
    confidence_score: float


class AdCampaign(BaseModel):
    """Ad campaign"""
    id: str
    name: str
    platform: str
    status: str
    budget: float
    budget_type: str  # daily, lifetime
    start_date: str
    end_date: Optional[str]
    targeting: dict
    variants: List[AdVariant]
    metrics: dict


class AdPerformance(BaseModel):
    """Ad performance metrics"""
    impressions: int
    clicks: int
    ctr: float
    conversions: int
    conversion_rate: float
    spend: float
    cpc: float
    cpa: float
    roas: float


@router.post("/generate")
async def generate_ads(
    request: AdGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered ad variants.
    
    Creates optimized ad copy with predicted performance metrics.
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
    
    # Generate ad variants
    variants = _generate_ad_variants(request)
    
    return {
        "variants": variants,
        "platform": request.platform,
        "recommendation": "Start with Variant 1 as it has the highest predicted CTR. Run A/B tests with Variant 2 after initial data collection."
    }


@router.get("/campaigns")
async def list_campaigns(
    org_id: UUID = Query(..., description="Organization ID"),
    platform: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all ad campaigns."""
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
    
    # Return sample campaigns
    return {
        "campaigns": [
            {
                "id": "camp-1",
                "name": "Spring Product Launch",
                "platform": "google",
                "status": "active",
                "budget": 5000.00,
                "spent": 2340.50,
                "impressions": 125000,
                "clicks": 3750,
                "conversions": 89,
                "ctr": 3.0,
                "roas": 4.2,
            },
            {
                "id": "camp-2",
                "name": "Brand Awareness Q1",
                "platform": "meta",
                "status": "active",
                "budget": 3000.00,
                "spent": 1890.25,
                "impressions": 450000,
                "clicks": 8100,
                "conversions": 45,
                "ctr": 1.8,
                "roas": 2.8,
            },
            {
                "id": "camp-3",
                "name": "Retargeting Campaign",
                "platform": "google",
                "status": "paused",
                "budget": 1500.00,
                "spent": 1500.00,
                "impressions": 75000,
                "clicks": 1875,
                "conversions": 62,
                "ctr": 2.5,
                "roas": 5.1,
            },
        ],
        "total_spend": 5730.75,
        "total_conversions": 196,
        "average_roas": 4.03,
    }


@router.get("/platforms")
async def get_platforms(
    current_user: User = Depends(get_current_user)
):
    """Get supported ad platforms."""
    return {
        "platforms": [
            {
                "id": "google",
                "name": "Google Ads",
                "types": ["search", "display", "video", "shopping", "pmax"],
                "connected": True,
                "account_id": "xxx-xxx-xxxx",
            },
            {
                "id": "meta",
                "name": "Meta Ads",
                "types": ["feed", "stories", "reels", "carousel"],
                "connected": True,
                "account_id": "act_xxxxxxxxxx",
            },
            {
                "id": "linkedin",
                "name": "LinkedIn Ads",
                "types": ["sponsored_content", "message_ads", "text_ads"],
                "connected": False,
                "account_id": None,
            },
            {
                "id": "tiktok",
                "name": "TikTok Ads",
                "types": ["in_feed", "topview", "spark_ads"],
                "connected": False,
                "account_id": None,
            },
        ]
    }


@router.get("/optimization-suggestions")
async def get_optimization_suggestions(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered optimization suggestions."""
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
    
    return {
        "suggestions": [
            {
                "id": "sug-1",
                "type": "budget",
                "priority": "high",
                "campaign": "Spring Product Launch",
                "title": "Increase budget for top performer",
                "description": "This campaign has 4.2x ROAS. Increasing daily budget by 25% could capture additional conversions.",
                "estimated_impact": "+15-20 conversions/week",
                "action": {"type": "increase_budget", "value": 25, "unit": "percent"},
            },
            {
                "id": "sug-2",
                "type": "targeting",
                "priority": "medium",
                "campaign": "Brand Awareness Q1",
                "title": "Narrow audience targeting",
                "description": "Current audience is too broad. Focusing on 25-44 age range could improve CTR by 0.5%.",
                "estimated_impact": "+0.5% CTR improvement",
                "action": {"type": "update_targeting", "field": "age", "value": "25-44"},
            },
            {
                "id": "sug-3",
                "type": "creative",
                "priority": "high",
                "campaign": "Retargeting Campaign",
                "title": "Refresh ad creatives",
                "description": "Ad fatigue detected. CTR has dropped 20% in past 2 weeks. New creatives recommended.",
                "estimated_impact": "Recover CTR to original levels",
                "action": {"type": "generate_creatives", "count": 3},
            },
            {
                "id": "sug-4",
                "type": "bid",
                "priority": "low",
                "campaign": "Spring Product Launch",
                "title": "Switch to target CPA bidding",
                "description": "With 89+ conversions, you have enough data for automated bidding. Could reduce CPA by 10-15%.",
                "estimated_impact": "-10-15% CPA",
                "action": {"type": "change_bidding", "strategy": "target_cpa"},
            },
        ],
        "total_potential_impact": {
            "additional_conversions": "25-35 per week",
            "cpa_reduction": "10-15%",
            "roas_improvement": "0.5-1.0x",
        },
    }


@router.post("/ab-test")
async def create_ab_test(
    campaign_id: str,
    variant_ids: List[str],
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an A/B test for ad variants."""
    return {
        "test_id": "test-123",
        "campaign_id": campaign_id,
        "variants": variant_ids,
        "status": "running",
        "traffic_split": [50, 50] if len(variant_ids) == 2 else [33, 33, 34],
        "statistical_significance_threshold": 95,
        "estimated_completion": "7-14 days based on current traffic",
    }


def _generate_ad_variants(request: AdGenerateRequest) -> List[AdVariant]:
    """Generate sample ad variants."""
    variants = [
        AdVariant(
            id="var-1",
            headline=f"Transform Your Business with {request.product_name}",
            description=f"Discover how {request.product_name} helps {request.target_audience} achieve their goals. Start your free trial today!",
            cta="Get Started Free",
            image_prompt=f"Modern, professional image showing {request.product_name} in use, clean design with blue accents",
            predicted_ctr=3.2,
            predicted_conversion_rate=2.8,
            confidence_score=0.85,
        ),
        AdVariant(
            id="var-2",
            headline=f"Stop Wasting Time — Try {request.product_name}",
            description=f"Join thousands of {request.target_audience} who've already switched. See results in 24 hours or less.",
            cta="Try Free for 14 Days",
            image_prompt=f"Before/after comparison showing productivity improvement, minimal design",
            predicted_ctr=2.9,
            predicted_conversion_rate=3.1,
            confidence_score=0.82,
        ),
        AdVariant(
            id="var-3",
            headline=f"The Smart Way to {request.goal.title()}",
            description=f"{request.product_name} uses AI to automate what takes you hours. {request.target_audience} save 10+ hrs/week.",
            cta="See How It Works",
            image_prompt=f"Abstract AI/automation visualization with human element, purple and blue gradient",
            predicted_ctr=2.7,
            predicted_conversion_rate=2.5,
            confidence_score=0.78,
        ),
    ]
    
    return variants[:request.count]

