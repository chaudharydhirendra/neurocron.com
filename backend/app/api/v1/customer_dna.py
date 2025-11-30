"""
NeuroCron CustomerDNA API
Unified Customer Data Platform endpoints
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.customer import CustomerProfile, CustomerEvent, CustomerSegment, CustomerJourney

router = APIRouter()


# === Schemas ===

class CustomerCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    external_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    custom_attributes: Optional[dict] = None
    tags: Optional[List[str]] = None


class CustomerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    custom_attributes: Optional[dict] = None
    tags: Optional[List[str]] = None


class EventTrack(BaseModel):
    event_type: str
    event_name: str
    source: str = "api"
    channel: Optional[str] = None
    campaign_id: Optional[str] = None
    page_url: Optional[str] = None
    value: Optional[float] = 0.0
    properties: Optional[dict] = None


class SegmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rules: Optional[dict] = None
    is_dynamic: bool = False


# === Helpers ===

async def verify_org_access(
    org_id: UUID,
    user_id: UUID,
    db: AsyncSession
) -> bool:
    """Verify user has access to organization."""
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Customer Endpoints ===

@router.get("/customers")
async def list_customers(
    org_id: UUID = Query(...),
    search: Optional[str] = None,
    segment_id: Optional[UUID] = None,
    min_score: Optional[int] = None,
    max_churn_risk: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customers with filtering and search."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Build query
    query = select(CustomerProfile).where(CustomerProfile.organization_id == org_id)
    
    if search:
        query = query.where(
            or_(
                CustomerProfile.email.ilike(f"%{search}%"),
                CustomerProfile.first_name.ilike(f"%{search}%"),
                CustomerProfile.last_name.ilike(f"%{search}%"),
                CustomerProfile.company_name.ilike(f"%{search}%"),
            )
        )
    
    if min_score is not None:
        query = query.where(CustomerProfile.engagement_score >= min_score)
    
    if max_churn_risk is not None:
        query = query.where(CustomerProfile.churn_risk <= max_churn_risk)
    
    # Count total
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Get customers
    query = query.order_by(CustomerProfile.last_seen_at.desc().nullslast())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    customers = result.scalars().all()
    
    return {
        "customers": [
            {
                "id": str(c.id),
                "email": c.email,
                "first_name": c.first_name,
                "last_name": c.last_name,
                "full_name": f"{c.first_name or ''} {c.last_name or ''}".strip() or c.email,
                "company_name": c.company_name,
                "engagement_score": c.engagement_score,
                "churn_risk": c.churn_risk,
                "lifetime_value": c.lifetime_value,
                "total_orders": c.total_orders,
                "last_seen_at": c.last_seen_at.isoformat() if c.last_seen_at else None,
                "acquisition_source": c.acquisition_source,
                "tags": c.tags or [],
            }
            for c in customers
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/customers")
async def create_customer(
    customer: CustomerCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update a customer profile."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check for existing customer by email or external_id
    existing = None
    if customer.email:
        result = await db.execute(
            select(CustomerProfile)
            .where(CustomerProfile.organization_id == org_id)
            .where(CustomerProfile.email == customer.email)
        )
        existing = result.scalar_one_or_none()
    
    if not existing and customer.external_id:
        result = await db.execute(
            select(CustomerProfile)
            .where(CustomerProfile.organization_id == org_id)
            .where(CustomerProfile.external_id == customer.external_id)
        )
        existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing
        if customer.first_name:
            existing.first_name = customer.first_name
        if customer.last_name:
            existing.last_name = customer.last_name
        if customer.phone:
            existing.phone = customer.phone
        if customer.company_name:
            existing.company_name = customer.company_name
        if customer.custom_attributes:
            existing.custom_attributes = {
                **(existing.custom_attributes or {}),
                **customer.custom_attributes
            }
        if customer.tags:
            existing.tags = list(set((existing.tags or []) + customer.tags))
        
        await db.commit()
        await db.refresh(existing)
        
        return {"id": str(existing.id), "message": "Customer updated", "is_new": False}
    
    # Create new
    new_customer = CustomerProfile(
        organization_id=org_id,
        email=customer.email,
        phone=customer.phone,
        external_id=customer.external_id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        company_name=customer.company_name,
        custom_attributes=customer.custom_attributes or {},
        tags=customer.tags or [],
        first_seen_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow(),
        acquisition_date=datetime.utcnow(),
    )
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    return {"id": str(new_customer.id), "message": "Customer created", "is_new": True}


@router.get("/customers/{customer_id}")
async def get_customer(
    customer_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed customer profile."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.id == customer_id)
        .where(CustomerProfile.organization_id == org_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get recent events
    events_result = await db.execute(
        select(CustomerEvent)
        .where(CustomerEvent.customer_id == customer_id)
        .order_by(CustomerEvent.occurred_at.desc())
        .limit(20)
    )
    events = events_result.scalars().all()
    
    # Get journey
    journey_result = await db.execute(
        select(CustomerJourney).where(CustomerJourney.customer_id == customer_id)
    )
    journey = journey_result.scalar_one_or_none()
    
    return {
        "id": str(customer.id),
        "email": customer.email,
        "phone": customer.phone,
        "external_id": customer.external_id,
        "first_name": customer.first_name,
        "last_name": customer.last_name,
        "full_name": f"{customer.first_name or ''} {customer.last_name or ''}".strip(),
        "company_name": customer.company_name,
        "job_title": customer.job_title,
        "industry": customer.industry,
        "location": {
            "city": customer.location_city,
            "country": customer.location_country,
            "timezone": customer.timezone,
        },
        "demographics": {
            "age_range": customer.age_range,
            "gender": customer.gender,
            "language": customer.language,
        },
        "engagement": {
            "total_sessions": customer.total_sessions,
            "total_page_views": customer.total_page_views,
            "total_events": customer.total_events,
            "total_email_opens": customer.total_email_opens,
            "total_email_clicks": customer.total_email_clicks,
        },
        "revenue": {
            "total_orders": customer.total_orders,
            "total_revenue": customer.total_revenue,
            "average_order_value": customer.average_order_value,
            "lifetime_value": customer.lifetime_value,
        },
        "scores": {
            "engagement": customer.engagement_score,
            "purchase_likelihood": customer.purchase_likelihood,
            "churn_risk": customer.churn_risk,
            "customer_fit": customer.customer_fit_score,
        },
        "acquisition": {
            "source": customer.acquisition_source,
            "campaign": customer.acquisition_campaign,
            "date": customer.acquisition_date.isoformat() if customer.acquisition_date else None,
        },
        "preferences": {
            "email_opt_in": customer.email_opt_in,
            "sms_opt_in": customer.sms_opt_in,
            "push_opt_in": customer.push_opt_in,
        },
        "segments": customer.segments or [],
        "tags": customer.tags or [],
        "custom_attributes": customer.custom_attributes or {},
        "timestamps": {
            "first_seen": customer.first_seen_at.isoformat() if customer.first_seen_at else None,
            "last_seen": customer.last_seen_at.isoformat() if customer.last_seen_at else None,
            "last_purchase": customer.last_purchase_at.isoformat() if customer.last_purchase_at else None,
        },
        "journey": {
            "current_stage": journey.current_stage if journey else "unknown",
            "is_stalled": journey.is_stalled if journey else False,
            "velocity_score": journey.velocity_score if journey else 50,
        } if journey else None,
        "recent_events": [
            {
                "type": e.event_type,
                "name": e.event_name,
                "source": e.source,
                "channel": e.channel,
                "occurred_at": e.occurred_at.isoformat(),
                "value": e.value,
            }
            for e in events
        ],
    }


@router.put("/customers/{customer_id}")
async def update_customer(
    customer_id: UUID,
    updates: CustomerUpdate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customer profile."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.id == customer_id)
        .where(CustomerProfile.organization_id == org_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Apply updates
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(customer, key, value)
    
    await db.commit()
    
    return {"message": "Customer updated"}


# === Event Tracking ===

@router.post("/customers/{customer_id}/events")
async def track_event(
    customer_id: UUID,
    event: EventTrack,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Track a customer event."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify customer exists
    result = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.id == customer_id)
        .where(CustomerProfile.organization_id == org_id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Create event
    new_event = CustomerEvent(
        customer_id=customer_id,
        organization_id=org_id,
        event_type=event.event_type,
        event_name=event.event_name,
        source=event.source,
        channel=event.channel,
        campaign_id=event.campaign_id,
        page_url=event.page_url,
        value=event.value or 0.0,
        properties=event.properties or {},
        occurred_at=datetime.utcnow(),
    )
    db.add(new_event)
    
    # Update customer stats
    customer.total_events += 1
    customer.last_seen_at = datetime.utcnow()
    
    if event.event_type == "page_view":
        customer.total_page_views += 1
    elif event.event_type == "session_start":
        customer.total_sessions += 1
    elif event.event_type == "email_open":
        customer.total_email_opens += 1
    elif event.event_type == "email_click":
        customer.total_email_clicks += 1
    elif event.event_type == "purchase":
        customer.total_orders += 1
        customer.total_revenue += event.value or 0
        customer.last_purchase_at = datetime.utcnow()
        if customer.total_orders > 0:
            customer.average_order_value = customer.total_revenue / customer.total_orders
    
    await db.commit()
    
    return {"message": "Event tracked", "event_id": str(new_event.id)}


@router.get("/customers/{customer_id}/timeline")
async def get_customer_timeline(
    customer_id: UUID,
    org_id: UUID = Query(...),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer event timeline."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(CustomerEvent)
        .where(CustomerEvent.customer_id == customer_id)
        .where(CustomerEvent.organization_id == org_id)
        .order_by(CustomerEvent.occurred_at.desc())
        .limit(limit)
    )
    events = result.scalars().all()
    
    return {
        "timeline": [
            {
                "id": str(e.id),
                "type": e.event_type,
                "name": e.event_name,
                "source": e.source,
                "channel": e.channel,
                "campaign_id": e.campaign_id,
                "page_url": e.page_url,
                "value": e.value,
                "properties": e.properties,
                "occurred_at": e.occurred_at.isoformat(),
            }
            for e in events
        ]
    }


# === Segments ===

@router.get("/segments")
async def list_segments(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List customer segments."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(CustomerSegment)
        .where(CustomerSegment.organization_id == org_id)
        .where(CustomerSegment.is_active == True)
        .order_by(CustomerSegment.created_at.desc())
    )
    segments = result.scalars().all()
    
    return {
        "segments": [
            {
                "id": str(s.id),
                "name": s.name,
                "description": s.description,
                "type": s.segment_type,
                "member_count": s.member_count,
                "is_dynamic": s.is_dynamic,
                "last_computed_at": s.last_computed_at.isoformat() if s.last_computed_at else None,
            }
            for s in segments
        ]
    }


@router.post("/segments")
async def create_segment(
    segment: SegmentCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a customer segment."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_segment = CustomerSegment(
        organization_id=org_id,
        name=segment.name,
        description=segment.description,
        segment_type="rules" if segment.rules else "manual",
        rules=segment.rules or {},
        is_dynamic=segment.is_dynamic,
    )
    db.add(new_segment)
    await db.commit()
    await db.refresh(new_segment)
    
    return {"id": str(new_segment.id), "message": "Segment created"}


# === Analytics ===

@router.get("/analytics/overview")
async def get_cdp_overview(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get CustomerDNA overview metrics."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Total customers
    total_result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.organization_id == org_id)
    )
    total_customers = total_result.scalar() or 0
    
    # Active last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.organization_id == org_id)
        .where(CustomerProfile.last_seen_at >= thirty_days_ago)
    )
    active_customers = active_result.scalar() or 0
    
    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(CustomerProfile.total_revenue))
        .where(CustomerProfile.organization_id == org_id)
    )
    total_revenue = revenue_result.scalar() or 0
    
    # Average engagement score
    engagement_result = await db.execute(
        select(func.avg(CustomerProfile.engagement_score))
        .where(CustomerProfile.organization_id == org_id)
    )
    avg_engagement = round(engagement_result.scalar() or 50)
    
    # High churn risk count
    churn_result = await db.execute(
        select(func.count(CustomerProfile.id))
        .where(CustomerProfile.organization_id == org_id)
        .where(CustomerProfile.churn_risk >= 70)
    )
    high_churn_risk = churn_result.scalar() or 0
    
    return {
        "total_customers": total_customers,
        "active_customers_30d": active_customers,
        "total_revenue": round(total_revenue, 2),
        "average_engagement_score": avg_engagement,
        "high_churn_risk_count": high_churn_risk,
        "acquisition_sources": {
            "organic": 35,
            "paid": 28,
            "referral": 22,
            "direct": 15,
        },
        "top_segments": [
            {"name": "High Value", "count": int(total_customers * 0.15)},
            {"name": "At Risk", "count": int(total_customers * 0.08)},
            {"name": "New Users", "count": int(total_customers * 0.25)},
        ],
    }


@router.get("/analytics/cohorts")
async def get_cohort_analysis(
    org_id: UUID = Query(...),
    metric: str = Query("retention", enum=["retention", "revenue", "engagement"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get cohort analysis data."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Sample cohort data (in production, calculate from events)
    cohorts = []
    for i in range(6):
        month = (datetime.utcnow() - timedelta(days=30 * i)).strftime("%B %Y")
        cohorts.append({
            "cohort": month,
            "size": 100 - (i * 10),
            "week_1": 100 - (i * 5),
            "week_2": 85 - (i * 5),
            "week_3": 70 - (i * 5),
            "week_4": 60 - (i * 5),
            "week_8": 45 - (i * 5),
            "week_12": 35 - (i * 5),
        })
    
    return {"cohorts": cohorts, "metric": metric}

