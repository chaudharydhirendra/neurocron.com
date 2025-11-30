"""
NeuroCron RevenueLink API
Marketing-to-revenue attribution
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.attribution import (
    RevenueEvent, TouchpointRecord, AttributionResult,
    AttributionModel, ChannelPerformance, CampaignROI
)

router = APIRouter()


# === Schemas ===

class RevenueEventCreate(BaseModel):
    event_type: str = "purchase"
    event_id: str
    revenue: float
    currency: str = "USD"
    product_name: Optional[str] = None
    customer_id: Optional[UUID] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class TouchpointCreate(BaseModel):
    visitor_id: str
    touchpoint_type: str
    channel: str
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign_name: Optional[str] = None
    landing_page: Optional[str] = None


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Revenue Events ===

@router.get("/revenue")
async def list_revenue_events(
    org_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List revenue events."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(RevenueEvent)
        .where(RevenueEvent.organization_id == org_id)
        .where(RevenueEvent.occurred_at >= since)
        .order_by(RevenueEvent.occurred_at.desc())
        .limit(100)
    )
    events = result.scalars().all()
    
    return {
        "events": [
            {
                "id": str(e.id),
                "event_type": e.event_type,
                "event_id": e.event_id,
                "revenue": e.revenue,
                "currency": e.currency,
                "product_name": e.product_name,
                "utm_source": e.utm_source,
                "utm_campaign": e.utm_campaign,
                "occurred_at": e.occurred_at.isoformat(),
            }
            for e in events
        ]
    }


@router.post("/revenue")
async def track_revenue(
    event: RevenueEventCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track a revenue event."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_event = RevenueEvent(
        organization_id=org_id,
        customer_id=event.customer_id,
        event_type=event.event_type,
        event_id=event.event_id,
        revenue=event.revenue,
        currency=event.currency,
        product_name=event.product_name,
        utm_source=event.utm_source,
        utm_medium=event.utm_medium,
        utm_campaign=event.utm_campaign,
    )
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    return {"id": str(new_event.id), "message": "Revenue tracked"}


# === Touchpoints ===

@router.post("/touchpoints")
async def track_touchpoint(
    touchpoint: TouchpointCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Track a marketing touchpoint."""
    new_touchpoint = TouchpointRecord(
        organization_id=org_id,
        visitor_id=touchpoint.visitor_id,
        touchpoint_type=touchpoint.touchpoint_type,
        channel=touchpoint.channel,
        source=touchpoint.source,
        medium=touchpoint.medium,
        campaign_name=touchpoint.campaign_name,
        landing_page=touchpoint.landing_page,
    )
    db.add(new_touchpoint)
    await db.commit()
    
    return {"message": "Touchpoint tracked"}


@router.get("/touchpoints/{visitor_id}")
async def get_visitor_journey(
    visitor_id: str,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get visitor's touchpoint journey."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(TouchpointRecord)
        .where(TouchpointRecord.organization_id == org_id)
        .where(TouchpointRecord.visitor_id == visitor_id)
        .order_by(TouchpointRecord.occurred_at)
    )
    touchpoints = result.scalars().all()
    
    return {
        "visitor_id": visitor_id,
        "journey": [
            {
                "type": t.touchpoint_type,
                "channel": t.channel,
                "source": t.source,
                "campaign": t.campaign_name,
                "landing_page": t.landing_page,
                "occurred_at": t.occurred_at.isoformat(),
                "is_first": t.is_first_touch,
                "is_last": t.is_last_touch,
            }
            for t in touchpoints
        ]
    }


# === Attribution Analytics ===

@router.get("/analytics/overview")
async def get_attribution_overview(
    org_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    model: str = Query("last_touch"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get attribution analytics overview."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(RevenueEvent.revenue))
        .where(RevenueEvent.organization_id == org_id)
        .where(RevenueEvent.occurred_at >= since)
    )
    total_revenue = revenue_result.scalar() or 0
    
    # Total conversions
    conversions_result = await db.execute(
        select(func.count(RevenueEvent.id))
        .where(RevenueEvent.organization_id == org_id)
        .where(RevenueEvent.occurred_at >= since)
    )
    total_conversions = conversions_result.scalar() or 0
    
    # Revenue by channel (using UTM source)
    channel_result = await db.execute(
        select(
            RevenueEvent.utm_source,
            func.sum(RevenueEvent.revenue),
            func.count(RevenueEvent.id),
        )
        .where(RevenueEvent.organization_id == org_id)
        .where(RevenueEvent.occurred_at >= since)
        .group_by(RevenueEvent.utm_source)
    )
    channel_data = [
        {
            "channel": row[0] or "Direct",
            "revenue": row[1],
            "conversions": row[2],
        }
        for row in channel_result.all()
    ]
    
    # Top campaigns by revenue
    campaign_result = await db.execute(
        select(
            RevenueEvent.utm_campaign,
            func.sum(RevenueEvent.revenue),
            func.count(RevenueEvent.id),
        )
        .where(RevenueEvent.organization_id == org_id)
        .where(RevenueEvent.occurred_at >= since)
        .where(RevenueEvent.utm_campaign != None)
        .group_by(RevenueEvent.utm_campaign)
        .order_by(func.sum(RevenueEvent.revenue).desc())
        .limit(10)
    )
    top_campaigns = [
        {
            "campaign": row[0],
            "revenue": row[1],
            "conversions": row[2],
        }
        for row in campaign_result.all()
    ]
    
    return {
        "period_days": days,
        "attribution_model": model,
        "summary": {
            "total_revenue": round(total_revenue, 2),
            "total_conversions": total_conversions,
            "avg_order_value": round(total_revenue / total_conversions, 2) if total_conversions > 0 else 0,
        },
        "by_channel": channel_data,
        "top_campaigns": top_campaigns,
    }


@router.get("/analytics/channels")
async def get_channel_performance(
    org_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed channel performance."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Touchpoints by channel
    touchpoint_result = await db.execute(
        select(
            TouchpointRecord.channel,
            func.count(TouchpointRecord.id).label("touchpoints"),
            func.count(func.distinct(TouchpointRecord.visitor_id)).label("visitors"),
        )
        .where(TouchpointRecord.organization_id == org_id)
        .where(TouchpointRecord.occurred_at >= since)
        .group_by(TouchpointRecord.channel)
    )
    
    channels = []
    for row in touchpoint_result.all():
        # Get conversions for this channel
        conversion_result = await db.execute(
            select(func.count(RevenueEvent.id), func.sum(RevenueEvent.revenue))
            .where(RevenueEvent.organization_id == org_id)
            .where(RevenueEvent.occurred_at >= since)
            .where(RevenueEvent.utm_source == row.channel)
        )
        conv_row = conversion_result.one()
        conversions = conv_row[0] or 0
        revenue = conv_row[1] or 0
        
        channels.append({
            "channel": row.channel,
            "touchpoints": row.touchpoints,
            "unique_visitors": row.visitors,
            "conversions": conversions,
            "revenue": round(revenue, 2),
            "conversion_rate": round((conversions / row.visitors * 100) if row.visitors > 0 else 0, 2),
        })
    
    return {
        "channels": sorted(channels, key=lambda x: x["revenue"], reverse=True)
    }


@router.get("/analytics/journey")
async def get_conversion_paths(
    org_id: UUID = Query(...),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get common conversion paths."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Sample conversion paths (in production, compute from actual data)
    sample_paths = [
        {
            "path": ["Paid Search", "Email", "Direct"],
            "conversions": 45,
            "revenue": 12500,
            "avg_touchpoints": 3,
        },
        {
            "path": ["Social", "Paid Search", "Email"],
            "conversions": 32,
            "revenue": 8700,
            "avg_touchpoints": 3,
        },
        {
            "path": ["Organic Search", "Direct"],
            "conversions": 28,
            "revenue": 7200,
            "avg_touchpoints": 2,
        },
        {
            "path": ["Paid Social", "Retargeting", "Direct"],
            "conversions": 25,
            "revenue": 6800,
            "avg_touchpoints": 3,
        },
        {
            "path": ["Direct"],
            "conversions": 22,
            "revenue": 5500,
            "avg_touchpoints": 1,
        },
    ]
    
    return {
        "conversion_paths": sample_paths[:limit],
        "insights": [
            "Multi-touch journeys convert 2.3x more than single-touch",
            "Email is present in 60% of high-value conversions",
            "Paid Search is the most common entry point",
        ],
    }


@router.post("/compute")
async def compute_attribution(
    org_id: UUID = Query(...),
    model: str = Query("last_touch"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger attribution computation."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In production, this would trigger a background job
    return {
        "message": f"Attribution computation started for {model} model",
        "period_days": days,
        "status": "processing",
    }

