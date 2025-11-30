"""
NeuroCron RetentionAI API
Churn prediction, retention campaigns, and loyalty programs
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.retention import (
    ChurnPrediction, ChurnRiskLevel, RetentionCampaign, RetentionAction,
    LoyaltyProgram, CustomerLoyalty, LoyaltyTransaction
)

router = APIRouter()


# === Schemas ===

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_risk_level: str = "high"
    trigger_min_score: int = 70
    campaign_type: str = "email"
    email_subject: Optional[str] = None
    email_template: Optional[str] = None
    offer_type: Optional[str] = None
    offer_value: Optional[str] = None


class LoyaltyProgramCreate(BaseModel):
    name: str = "Rewards Program"
    points_name: str = "Points"
    points_per_dollar: float = 1.0
    points_per_referral: int = 100
    tiers: List[dict] = []
    rewards: List[dict] = []


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Churn Predictions ===

@router.get("/predictions")
async def list_churn_predictions(
    org_id: UUID = Query(...),
    risk_level: Optional[str] = None,
    min_score: int = Query(0, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customers with churn predictions."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = (
        select(ChurnPrediction, CustomerProfile)
        .join(CustomerProfile, ChurnPrediction.customer_id == CustomerProfile.id)
        .where(ChurnPrediction.organization_id == org_id)
        .where(ChurnPrediction.risk_score >= min_score)
    )
    
    if risk_level:
        try:
            level = ChurnRiskLevel(risk_level.lower())
            query = query.where(ChurnPrediction.risk_level == level)
        except ValueError:
            pass
    
    query = query.order_by(ChurnPrediction.risk_score.desc()).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    return {
        "predictions": [
            {
                "customer_id": str(pred.customer_id),
                "customer_name": f"{cust.first_name or ''} {cust.last_name or ''}".strip() or cust.email,
                "customer_email": cust.email,
                "risk_score": pred.risk_score,
                "risk_level": pred.risk_level.value,
                "probability": pred.probability,
                "risk_factors": pred.risk_factors,
                "days_since_activity": pred.days_since_last_activity,
                "engagement_trend": pred.engagement_trend,
                "computed_at": pred.computed_at.isoformat(),
            }
            for pred, cust in rows
        ]
    }


@router.post("/predictions/compute")
async def compute_churn_predictions(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger churn prediction computation for all customers."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all customers
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.organization_id == org_id)
    )
    customers = result.scalars().all()
    
    computed = 0
    for customer in customers:
        # Calculate risk score based on engagement signals
        risk_factors = []
        base_score = 0
        
        # Days since last seen
        if customer.last_seen_at:
            days_inactive = (datetime.utcnow() - customer.last_seen_at).days
            if days_inactive > 60:
                base_score += 40
                risk_factors.append({"factor": "inactivity", "weight": 0.4, "description": f"No activity in {days_inactive} days"})
            elif days_inactive > 30:
                base_score += 25
                risk_factors.append({"factor": "declining_engagement", "weight": 0.25, "description": f"Low activity ({days_inactive} days ago)"})
            elif days_inactive > 14:
                base_score += 10
        else:
            base_score += 30
            risk_factors.append({"factor": "unknown_activity", "weight": 0.3, "description": "Never seen on platform"})
        
        # Engagement score impact
        if customer.engagement_score < 30:
            base_score += 25
            risk_factors.append({"factor": "low_engagement", "weight": 0.25, "description": f"Engagement score: {customer.engagement_score}"})
        elif customer.engagement_score < 50:
            base_score += 10
        
        # Purchase behavior
        if customer.total_orders == 0:
            base_score += 15
            risk_factors.append({"factor": "no_purchase", "weight": 0.15, "description": "No purchases"})
        elif customer.last_purchase_at:
            days_since_purchase = (datetime.utcnow() - customer.last_purchase_at).days
            if days_since_purchase > 90:
                base_score += 20
                risk_factors.append({"factor": "lapsed_buyer", "weight": 0.2, "description": f"Last purchase {days_since_purchase} days ago"})
        
        # Cap score at 100
        risk_score = min(100, base_score)
        
        # Determine risk level
        if risk_score >= 80:
            risk_level = ChurnRiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = ChurnRiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = ChurnRiskLevel.MEDIUM
        else:
            risk_level = ChurnRiskLevel.LOW
        
        # Check for existing prediction
        existing = await db.execute(
            select(ChurnPrediction).where(ChurnPrediction.customer_id == customer.id)
        )
        prediction = existing.scalar_one_or_none()
        
        if prediction:
            prediction.risk_score = risk_score
            prediction.risk_level = risk_level
            prediction.probability = risk_score / 100
            prediction.risk_factors = risk_factors
            prediction.computed_at = datetime.utcnow()
        else:
            prediction = ChurnPrediction(
                customer_id=customer.id,
                organization_id=org_id,
                risk_score=risk_score,
                risk_level=risk_level,
                probability=risk_score / 100,
                risk_factors=risk_factors,
            )
            db.add(prediction)
        
        # Update customer's churn_risk field
        customer.churn_risk = risk_score
        computed += 1
    
    await db.commit()
    
    return {"message": f"Computed predictions for {computed} customers"}


@router.get("/predictions/{customer_id}")
async def get_customer_churn_prediction(
    customer_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed churn prediction for a specific customer."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ChurnPrediction, CustomerProfile)
        .join(CustomerProfile, ChurnPrediction.customer_id == CustomerProfile.id)
        .where(ChurnPrediction.customer_id == customer_id)
        .where(ChurnPrediction.organization_id == org_id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    pred, cust = row
    
    return {
        "customer": {
            "id": str(cust.id),
            "name": f"{cust.first_name or ''} {cust.last_name or ''}".strip(),
            "email": cust.email,
            "lifetime_value": cust.lifetime_value,
        },
        "prediction": {
            "risk_score": pred.risk_score,
            "risk_level": pred.risk_level.value,
            "probability": pred.probability,
            "risk_factors": pred.risk_factors,
            "days_since_activity": pred.days_since_last_activity,
            "engagement_trend": pred.engagement_trend,
            "model_version": pred.model_version,
            "computed_at": pred.computed_at.isoformat(),
        },
        "recommendations": [
            {"action": "Send personalized offer", "impact": "high", "channel": "email"},
            {"action": "Assign to success team", "impact": "high", "channel": "outreach"},
            {"action": "Trigger win-back campaign", "impact": "medium", "channel": "email"},
        ],
    }


# === Retention Campaigns ===

@router.get("/campaigns")
async def list_retention_campaigns(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List retention campaigns."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(RetentionCampaign)
        .where(RetentionCampaign.organization_id == org_id)
        .order_by(RetentionCampaign.created_at.desc())
    )
    campaigns = result.scalars().all()
    
    return {
        "campaigns": [
            {
                "id": str(c.id),
                "name": c.name,
                "trigger_risk_level": c.trigger_risk_level.value,
                "trigger_min_score": c.trigger_min_score,
                "campaign_type": c.campaign_type,
                "offer_type": c.offer_type,
                "is_active": c.is_active,
                "stats": {
                    "sent": c.sent_count,
                    "opened": c.opened_count,
                    "clicked": c.clicked_count,
                    "converted": c.converted_count,
                    "open_rate": round((c.opened_count / c.sent_count * 100) if c.sent_count > 0 else 0, 1),
                    "conversion_rate": round((c.converted_count / c.sent_count * 100) if c.sent_count > 0 else 0, 1),
                },
            }
            for c in campaigns
        ]
    }


@router.post("/campaigns")
async def create_retention_campaign(
    campaign: CampaignCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a retention campaign."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_campaign = RetentionCampaign(
        organization_id=org_id,
        name=campaign.name,
        description=campaign.description,
        trigger_risk_level=ChurnRiskLevel(campaign.trigger_risk_level.lower()),
        trigger_min_score=campaign.trigger_min_score,
        campaign_type=campaign.campaign_type,
        email_subject=campaign.email_subject,
        email_template=campaign.email_template,
        offer_type=campaign.offer_type,
        offer_value=campaign.offer_value,
    )
    db.add(new_campaign)
    await db.commit()
    await db.refresh(new_campaign)
    
    return {"id": str(new_campaign.id), "message": "Campaign created"}


# === Analytics ===

@router.get("/analytics/overview")
async def get_retention_overview(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get retention analytics overview."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Risk level distribution
    distribution = {}
    for level in ChurnRiskLevel:
        result = await db.execute(
            select(func.count(ChurnPrediction.id))
            .where(ChurnPrediction.organization_id == org_id)
            .where(ChurnPrediction.risk_level == level)
        )
        distribution[level.value] = result.scalar() or 0
    
    # Total at-risk customers
    at_risk = await db.execute(
        select(func.count(ChurnPrediction.id))
        .where(ChurnPrediction.organization_id == org_id)
        .where(ChurnPrediction.risk_score >= 60)
    )
    at_risk_count = at_risk.scalar() or 0
    
    # Revenue at risk
    revenue_result = await db.execute(
        select(func.sum(CustomerProfile.lifetime_value))
        .join(ChurnPrediction, CustomerProfile.id == ChurnPrediction.customer_id)
        .where(ChurnPrediction.organization_id == org_id)
        .where(ChurnPrediction.risk_score >= 60)
    )
    revenue_at_risk = revenue_result.scalar() or 0
    
    # Campaign stats
    campaign_result = await db.execute(
        select(
            func.sum(RetentionCampaign.sent_count),
            func.sum(RetentionCampaign.converted_count),
        )
        .where(RetentionCampaign.organization_id == org_id)
    )
    campaign_stats = campaign_result.one()
    
    return {
        "risk_distribution": distribution,
        "at_risk_customers": at_risk_count,
        "revenue_at_risk": round(revenue_at_risk, 2),
        "campaigns": {
            "total_sent": campaign_stats[0] or 0,
            "total_converted": campaign_stats[1] or 0,
            "conversion_rate": round((campaign_stats[1] / campaign_stats[0] * 100) if campaign_stats[0] else 0, 1),
        },
        "retention_rate": 85.2,  # Calculate from actual data
        "churn_rate": 14.8,
    }


# === Loyalty Program ===

@router.get("/loyalty/program")
async def get_loyalty_program(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization's loyalty program."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.organization_id == org_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        return {"program": None, "message": "No loyalty program configured"}
    
    # Get member stats
    members_result = await db.execute(
        select(func.count(CustomerLoyalty.id))
        .where(CustomerLoyalty.program_id == program.id)
    )
    member_count = members_result.scalar() or 0
    
    return {
        "program": {
            "id": str(program.id),
            "name": program.name,
            "points_name": program.points_name,
            "points_per_dollar": program.points_per_dollar,
            "tiers": program.tiers,
            "rewards": program.rewards,
            "is_active": program.is_active,
        },
        "stats": {
            "total_members": member_count,
        },
    }


@router.post("/loyalty/program")
async def create_loyalty_program(
    program: LoyaltyProgramCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update loyalty program."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check for existing
    existing = await db.execute(
        select(LoyaltyProgram).where(LoyaltyProgram.organization_id == org_id)
    )
    existing_program = existing.scalar_one_or_none()
    
    if existing_program:
        existing_program.name = program.name
        existing_program.points_name = program.points_name
        existing_program.points_per_dollar = program.points_per_dollar
        existing_program.tiers = program.tiers
        existing_program.rewards = program.rewards
        await db.commit()
        return {"id": str(existing_program.id), "message": "Loyalty program updated"}
    
    new_program = LoyaltyProgram(
        organization_id=org_id,
        name=program.name,
        points_name=program.points_name,
        points_per_dollar=program.points_per_dollar,
        tiers=program.tiers,
        rewards=program.rewards,
    )
    db.add(new_program)
    await db.commit()
    await db.refresh(new_program)
    
    return {"id": str(new_program.id), "message": "Loyalty program created"}

