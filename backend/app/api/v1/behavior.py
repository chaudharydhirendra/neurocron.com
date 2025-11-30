"""
NeuroCron BehaviorMind API
User behavior analytics, heatmaps, and session replay
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.behavior import (
    PageSession, ClickEvent, ScrollEvent, FormInteraction,
    HeatmapSnapshot, ConversionFunnel
)

router = APIRouter()


# === Schemas ===

class SessionTrack(BaseModel):
    visitor_id: str
    session_id: str
    page_url: str
    page_path: str
    page_title: Optional[str] = None
    referrer_url: Optional[str] = None
    device_type: str = "desktop"
    browser: Optional[str] = None
    os: Optional[str] = None
    screen_width: Optional[int] = None
    screen_height: Optional[int] = None
    viewport_width: Optional[int] = None
    viewport_height: Optional[int] = None
    country: Optional[str] = None
    city: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class ClickTrack(BaseModel):
    session_id: str
    x: int
    y: int
    page_x: int
    page_y: int
    element_tag: Optional[str] = None
    element_class: Optional[str] = None
    element_id: Optional[str] = None
    element_text: Optional[str] = None
    element_href: Optional[str] = None
    click_type: str = "click"


class ScrollTrack(BaseModel):
    session_id: str
    scroll_y: int
    scroll_depth_percent: int
    document_height: int


class FunnelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[dict]


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Session Tracking ===

@router.post("/sessions/start")
async def start_session(
    session: SessionTrack,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Start tracking a new page session."""
    new_session = PageSession(
        organization_id=org_id,
        visitor_id=session.visitor_id,
        session_id=session.session_id,
        page_url=session.page_url,
        page_path=session.page_path,
        page_title=session.page_title,
        referrer_url=session.referrer_url,
        device_type=session.device_type,
        browser=session.browser,
        os=session.os,
        screen_width=session.screen_width,
        screen_height=session.screen_height,
        viewport_width=session.viewport_width,
        viewport_height=session.viewport_height,
        country=session.country,
        city=session.city,
        utm_source=session.utm_source,
        utm_medium=session.utm_medium,
        utm_campaign=session.utm_campaign,
        started_at=datetime.utcnow(),
    )
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    return {"session_id": str(new_session.id), "message": "Session started"}


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: UUID,
    duration_seconds: int = Query(...),
    scroll_depth_max: int = Query(0),
    clicks_count: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    """End a page session with final metrics."""
    result = await db.execute(
        select(PageSession).where(PageSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.ended_at = datetime.utcnow()
    session.duration_seconds = duration_seconds
    session.scroll_depth_max = scroll_depth_max
    session.clicks_count = clicks_count
    session.is_bounce = duration_seconds < 10 and clicks_count == 0
    
    await db.commit()
    
    return {"message": "Session ended"}


@router.post("/clicks")
async def track_click(
    click: ClickTrack,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Track a click event."""
    # Find session by session_id string
    result = await db.execute(
        select(PageSession)
        .where(PageSession.session_id == click.session_id)
        .where(PageSession.organization_id == org_id)
        .order_by(PageSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return {"message": "Session not found, click not tracked"}
    
    new_click = ClickEvent(
        session_id=session.id,
        x=click.x,
        y=click.y,
        page_x=click.page_x,
        page_y=click.page_y,
        element_tag=click.element_tag,
        element_class=click.element_class,
        element_id=click.element_id,
        element_text=click.element_text[:255] if click.element_text else None,
        element_href=click.element_href,
        click_type=click.click_type,
        occurred_at=datetime.utcnow(),
    )
    db.add(new_click)
    await db.commit()
    
    return {"message": "Click tracked"}


@router.post("/scrolls")
async def track_scroll(
    scroll: ScrollTrack,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Track a scroll event."""
    result = await db.execute(
        select(PageSession)
        .where(PageSession.session_id == scroll.session_id)
        .where(PageSession.organization_id == org_id)
        .order_by(PageSession.started_at.desc())
    )
    session = result.scalar_one_or_none()
    
    if not session:
        return {"message": "Session not found"}
    
    new_scroll = ScrollEvent(
        session_id=session.id,
        scroll_y=scroll.scroll_y,
        scroll_depth_percent=scroll.scroll_depth_percent,
        document_height=scroll.document_height,
        occurred_at=datetime.utcnow(),
    )
    db.add(new_scroll)
    
    # Update max scroll depth
    if scroll.scroll_depth_percent > session.scroll_depth_max:
        session.scroll_depth_max = scroll.scroll_depth_percent
    
    await db.commit()
    
    return {"message": "Scroll tracked"}


# === Analytics Endpoints ===

@router.get("/analytics/overview")
async def get_behavior_overview(
    org_id: UUID = Query(...),
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get behavior analytics overview."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Total sessions
    sessions_result = await db.execute(
        select(func.count(PageSession.id))
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
    )
    total_sessions = sessions_result.scalar() or 0
    
    # Unique visitors
    visitors_result = await db.execute(
        select(func.count(func.distinct(PageSession.visitor_id)))
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
    )
    unique_visitors = visitors_result.scalar() or 0
    
    # Avg session duration
    duration_result = await db.execute(
        select(func.avg(PageSession.duration_seconds))
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
        .where(PageSession.duration_seconds > 0)
    )
    avg_duration = round(duration_result.scalar() or 0)
    
    # Bounce rate
    bounces_result = await db.execute(
        select(func.count(PageSession.id))
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
        .where(PageSession.is_bounce == True)
    )
    bounces = bounces_result.scalar() or 0
    bounce_rate = round((bounces / total_sessions * 100) if total_sessions > 0 else 0, 1)
    
    # Avg scroll depth
    scroll_result = await db.execute(
        select(func.avg(PageSession.scroll_depth_max))
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
    )
    avg_scroll = round(scroll_result.scalar() or 0)
    
    # Top pages
    pages_result = await db.execute(
        select(
            PageSession.page_path,
            func.count(PageSession.id).label("views"),
            func.avg(PageSession.duration_seconds).label("avg_time"),
        )
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
        .group_by(PageSession.page_path)
        .order_by(func.count(PageSession.id).desc())
        .limit(10)
    )
    top_pages = [
        {
            "path": row.page_path,
            "views": row.views,
            "avg_time": round(row.avg_time or 0),
        }
        for row in pages_result.all()
    ]
    
    # Device breakdown
    devices_result = await db.execute(
        select(
            PageSession.device_type,
            func.count(PageSession.id).label("count"),
        )
        .where(PageSession.organization_id == org_id)
        .where(PageSession.started_at >= since)
        .group_by(PageSession.device_type)
    )
    devices = {row.device_type: row.count for row in devices_result.all()}
    
    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "unique_visitors": unique_visitors,
        "avg_session_duration": avg_duration,
        "bounce_rate": bounce_rate,
        "avg_scroll_depth": avg_scroll,
        "top_pages": top_pages,
        "devices": devices,
    }


@router.get("/heatmaps/{page_path:path}")
async def get_heatmap(
    page_path: str,
    org_id: UUID = Query(...),
    heatmap_type: str = Query("click", enum=["click", "scroll", "move"]),
    device_type: str = Query("desktop", enum=["desktop", "mobile", "tablet"]),
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get heatmap data for a page."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check for cached snapshot
    result = await db.execute(
        select(HeatmapSnapshot)
        .where(HeatmapSnapshot.organization_id == org_id)
        .where(HeatmapSnapshot.page_path == f"/{page_path}")
        .where(HeatmapSnapshot.heatmap_type == heatmap_type)
        .where(HeatmapSnapshot.device_type == device_type)
        .order_by(HeatmapSnapshot.computed_at.desc())
    )
    snapshot = result.scalar_one_or_none()
    
    if snapshot and (datetime.utcnow() - snapshot.computed_at).days < 1:
        return {
            "page_path": snapshot.page_path,
            "heatmap_type": snapshot.heatmap_type,
            "device_type": snapshot.device_type,
            "data": snapshot.heatmap_data,
            "total_sessions": snapshot.total_sessions,
            "total_events": snapshot.total_events,
            "cached": True,
        }
    
    # Generate fresh heatmap data
    since = datetime.utcnow() - timedelta(days=days)
    
    if heatmap_type == "click":
        # Get click positions
        clicks_result = await db.execute(
            select(ClickEvent.page_x, ClickEvent.page_y)
            .join(PageSession, ClickEvent.session_id == PageSession.id)
            .where(PageSession.organization_id == org_id)
            .where(PageSession.page_path == f"/{page_path}")
            .where(PageSession.device_type == device_type)
            .where(PageSession.started_at >= since)
        )
        clicks = clicks_result.all()
        
        # Generate grid (simplified - in production, use more sophisticated algorithm)
        grid_size = 20
        heatmap_data = {}
        for click in clicks:
            grid_x = (click.page_x // grid_size) * grid_size
            grid_y = (click.page_y // grid_size) * grid_size
            key = f"{grid_x},{grid_y}"
            heatmap_data[key] = heatmap_data.get(key, 0) + 1
        
        return {
            "page_path": f"/{page_path}",
            "heatmap_type": heatmap_type,
            "device_type": device_type,
            "data": {
                "grid_size": grid_size,
                "points": [
                    {"x": int(k.split(",")[0]), "y": int(k.split(",")[1]), "value": v}
                    for k, v in sorted(heatmap_data.items(), key=lambda x: x[1], reverse=True)[:500]
                ],
            },
            "total_sessions": len(set(c.page_x for c in clicks)),
            "total_events": len(clicks),
            "cached": False,
        }
    
    return {
        "page_path": f"/{page_path}",
        "heatmap_type": heatmap_type,
        "device_type": device_type,
        "data": {"points": []},
        "message": "No data available",
    }


@router.get("/sessions")
async def list_sessions(
    org_id: UUID = Query(...),
    page_path: Optional[str] = None,
    device_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List recorded sessions."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(PageSession).where(PageSession.organization_id == org_id)
    
    if page_path:
        query = query.where(PageSession.page_path == page_path)
    if device_type:
        query = query.where(PageSession.device_type == device_type)
    
    query = query.order_by(PageSession.started_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return {
        "sessions": [
            {
                "id": str(s.id),
                "visitor_id": s.visitor_id,
                "page_path": s.page_path,
                "page_title": s.page_title,
                "device_type": s.device_type,
                "browser": s.browser,
                "country": s.country,
                "duration_seconds": s.duration_seconds,
                "scroll_depth": s.scroll_depth_max,
                "clicks_count": s.clicks_count,
                "is_bounce": s.is_bounce,
                "started_at": s.started_at.isoformat(),
            }
            for s in sessions
        ]
    }


# === Funnels ===

@router.get("/funnels")
async def list_funnels(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List conversion funnels."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ConversionFunnel)
        .where(ConversionFunnel.organization_id == org_id)
        .where(ConversionFunnel.is_active == True)
        .order_by(ConversionFunnel.created_at.desc())
    )
    funnels = result.scalars().all()
    
    return {
        "funnels": [
            {
                "id": str(f.id),
                "name": f.name,
                "description": f.description,
                "steps": f.steps,
                "total_entries": f.total_entries,
                "total_completions": f.total_completions,
                "conversion_rate": f.conversion_rate,
                "last_computed_at": f.last_computed_at.isoformat() if f.last_computed_at else None,
            }
            for f in funnels
        ]
    }


@router.post("/funnels")
async def create_funnel(
    funnel: FunnelCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a conversion funnel."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_funnel = ConversionFunnel(
        organization_id=org_id,
        name=funnel.name,
        description=funnel.description,
        steps=funnel.steps,
    )
    db.add(new_funnel)
    await db.commit()
    await db.refresh(new_funnel)
    
    return {"id": str(new_funnel.id), "message": "Funnel created"}

