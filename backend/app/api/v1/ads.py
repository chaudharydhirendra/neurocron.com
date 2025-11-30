"""
NeuroCron AdPilot API
Fully automated ad creation and management

AI Tier Used: Tier 2 - GPT-4.1 (best creative/ad copy generation)
"""

from typing import List, Optional
from uuid import UUID, uuid4
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.services.ai import ai_generator, PromptTemplates

logger = logging.getLogger(__name__)
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
    key_benefits: Optional[str] = None


class AdVariant(BaseModel):
    """Generated ad variant"""
    id: str
    variant_name: Optional[str] = None
    headline: str
    description: str
    cta: str
    image_prompt: Optional[str] = None
    video_concept: Optional[str] = None
    emotional_angle: Optional[str] = None
    predicted_ctr: float
    predicted_conversion_rate: float
    confidence_score: float
    best_for_audience: Optional[str] = None


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
    
    Uses Tier 2 (GPT-4.1) for best creative ad copy.
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
    
    # Get prompts for ad generation
    system_prompt, user_prompt = PromptTemplates.get_ad_prompt(
        product_name=request.product_name,
        product_description=request.product_description,
        target_audience=request.target_audience,
        platform=request.platform,
        ad_type=request.ad_type,
        goal=request.goal,
        count=request.count,
        benefits=request.key_benefits or "",
    )
    
    # Generate ads using AI (Tier 2: Creative - GPT-4.1)
    logger.info(f"Generating {request.count} ad variants for {request.product_name}")
    ai_response = await ai_generator.generate(
        task_type="ad_copy",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.85,  # Higher temperature for creative variety
        max_tokens=3000,
    )
    
    if not ai_response.success:
        logger.error(f"AI generation failed: {ai_response.error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ad generation failed: {ai_response.error}"
        )
    
    # Parse the AI response
    ads_data = ai_response.as_json
    if not ads_data:
        logger.error("Failed to parse AI response as JSON")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse ad response"
        )
    
    # Log cost for monitoring
    logger.info(
        f"Ads generated: model={ai_response.model_used}, "
        f"tokens_in={ai_response.tokens_in}, tokens_out={ai_response.tokens_out}, "
        f"cost=${ai_response.cost_estimate:.4f}"
    )
    
    # Build response
    variants = []
    for i, variant in enumerate(ads_data.get("variants", [])):
        variants.append(AdVariant(
            id=f"var-{uuid4()}",
            variant_name=variant.get("variant_name", f"Variant {i+1}"),
            headline=variant.get("headline", ""),
            description=variant.get("description", ""),
            cta=variant.get("cta", "Learn More"),
            image_prompt=variant.get("image_prompt"),
            video_concept=variant.get("video_concept"),
            emotional_angle=variant.get("emotional_angle"),
            predicted_ctr=float(variant.get("predicted_ctr", 2.0)),
            predicted_conversion_rate=float(variant.get("predicted_conversion_rate", 1.5)),
            confidence_score=float(variant.get("confidence_score", 0.8)),
            best_for_audience=variant.get("best_for_audience"),
        ))
    
    return {
        "variants": [v.model_dump() for v in variants],
        "platform": request.platform,
        "platform_notes": ads_data.get("platform_notes", ""),
        "recommendation": ads_data.get("recommended_test_plan", 
            "Start with the highest predicted CTR variant. Run A/B tests after 1000 impressions."),
        "budget_recommendation": ads_data.get("budget_recommendation", "$50-100/day for testing"),
        "ai_metadata": {
            "model": ai_response.model_used,
            "tier": ai_response.tier.value,
            "cost": ai_response.cost_estimate,
        }
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
    
    # TODO: Fetch real campaigns from connected ad platforms
    # For now, return placeholder indicating no campaigns yet
    return {
        "campaigns": [],
        "total_spend": 0,
        "total_conversions": 0,
        "average_roas": 0,
        "message": "Connect your ad platforms in Settings > Integrations to see campaigns here.",
    }


@router.get("/platforms")
async def get_platforms(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supported ad platforms and their connection status."""
    # TODO: Check actual connection status from IntegrationToken model
    return {
        "platforms": [
            {
                "id": "google",
                "name": "Google Ads",
                "types": ["search", "display", "video", "shopping", "pmax"],
                "connected": False,
                "account_id": None,
                "setup_url": "/settings?tab=integrations&connect=google",
            },
            {
                "id": "meta",
                "name": "Meta Ads",
                "types": ["feed", "stories", "reels", "carousel"],
                "connected": False,
                "account_id": None,
                "setup_url": "/settings?tab=integrations&connect=meta",
            },
            {
                "id": "linkedin",
                "name": "LinkedIn Ads",
                "types": ["sponsored_content", "message_ads", "text_ads"],
                "connected": False,
                "account_id": None,
                "setup_url": "/settings?tab=integrations&connect=linkedin",
            },
            {
                "id": "tiktok",
                "name": "TikTok Ads",
                "types": ["in_feed", "topview", "spark_ads"],
                "connected": False,
                "account_id": None,
                "setup_url": "/settings?tab=integrations&connect=tiktok",
            },
        ]
    }


@router.get("/optimization-suggestions")
async def get_optimization_suggestions(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered optimization suggestions for ad campaigns."""
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
    
    # TODO: Generate real suggestions based on connected campaign data
    return {
        "suggestions": [],
        "total_potential_impact": None,
        "message": "Connect your ad platforms to get AI-powered optimization suggestions.",
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
        "test_id": f"test-{uuid4()}",
        "campaign_id": campaign_id,
        "variants": variant_ids,
        "status": "pending_setup",
        "traffic_split": [50, 50] if len(variant_ids) == 2 else [33, 33, 34],
        "statistical_significance_threshold": 95,
        "message": "Connect your ad platform to activate this A/B test.",
    }


@router.get("/templates")
async def get_ad_templates(
    platform: Optional[str] = None,
    goal: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get ad templates for quick creation."""
    templates = [
        {
            "id": "product_launch",
            "name": "Product Launch",
            "description": "Announce a new product with impact",
            "platforms": ["meta", "google", "linkedin"],
            "goal": "awareness",
            "example_headline": "Introducing [Product]: The Future of [Category]",
            "example_cta": "Learn More",
        },
        {
            "id": "lead_gen",
            "name": "Lead Generation",
            "description": "Capture qualified leads with a compelling offer",
            "platforms": ["meta", "linkedin", "google"],
            "goal": "conversion",
            "example_headline": "Free [Resource]: Get [Benefit] Today",
            "example_cta": "Download Free",
        },
        {
            "id": "retargeting",
            "name": "Retargeting",
            "description": "Re-engage visitors who didn't convert",
            "platforms": ["meta", "google"],
            "goal": "conversion",
            "example_headline": "Still Thinking About [Product]?",
            "example_cta": "Complete Your Order",
        },
        {
            "id": "testimonial",
            "name": "Social Proof",
            "description": "Let customers sell for you",
            "platforms": ["meta", "linkedin", "tiktok"],
            "goal": "consideration",
            "example_headline": "See Why [X] Customers Love [Product]",
            "example_cta": "Read Reviews",
        },
        {
            "id": "limited_offer",
            "name": "Limited Time Offer",
            "description": "Create urgency with a time-bound offer",
            "platforms": ["meta", "google"],
            "goal": "conversion",
            "example_headline": "[X]% Off Ends [Day] - Don't Miss Out!",
            "example_cta": "Shop Now",
        },
    ]
    
    # Filter by platform and goal if provided
    if platform:
        templates = [t for t in templates if platform in t["platforms"]]
    if goal:
        templates = [t for t in templates if t["goal"] == goal]
    
    return {"templates": templates}
