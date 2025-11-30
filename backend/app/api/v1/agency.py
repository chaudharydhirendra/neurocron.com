"""
NeuroCron ClientSync API
Agency white-label mode
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.agency import AgencyClient, WhiteLabelConfig, ClientReport, ClientApproval

router = APIRouter()


# === Schemas ===

class ClientCreate(BaseModel):
    client_name: str
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    monthly_retainer: float = 0.0


class WhiteLabelUpdate(BaseModel):
    brand_name: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    custom_domain: Optional[str] = None
    hide_powered_by: bool = False


class ApprovalRequest(BaseModel):
    item_type: str
    item_id: UUID
    item_title: str
    message: Optional[str] = None


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Clients ===

@router.get("/clients")
async def list_clients(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List agency clients."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(AgencyClient)
        .where(AgencyClient.agency_id == org_id)
        .order_by(AgencyClient.created_at.desc())
    )
    clients = result.scalars().all()
    
    return {
        "clients": [
            {
                "id": str(c.id),
                "client_name": c.client_name,
                "client_logo_url": c.client_logo_url,
                "primary_contact_name": c.primary_contact_name,
                "primary_contact_email": c.primary_contact_email,
                "monthly_retainer": c.monthly_retainer,
                "status": c.status,
                "contract_start_date": c.contract_start_date.isoformat() if c.contract_start_date else None,
            }
            for c in clients
        ]
    }


@router.post("/clients")
async def create_client(
    client: ClientCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an agency client."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # In production, create a new organization for the client
    # For now, use a placeholder
    from app.models.organization import Organization
    
    client_org = Organization(
        name=client.client_name,
        plan="starter",
    )
    db.add(client_org)
    await db.flush()
    
    new_client = AgencyClient(
        agency_id=org_id,
        client_organization_id=client_org.id,
        client_name=client.client_name,
        primary_contact_name=client.primary_contact_name,
        primary_contact_email=client.primary_contact_email,
        monthly_retainer=client.monthly_retainer,
        contract_start_date=datetime.utcnow(),
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    
    return {"id": str(new_client.id), "message": "Client created"}


@router.get("/clients/{client_id}")
async def get_client(
    client_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get client details."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(AgencyClient)
        .where(AgencyClient.id == client_id)
        .where(AgencyClient.agency_id == org_id)
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Get pending approvals
    approvals_result = await db.execute(
        select(func.count(ClientApproval.id))
        .where(ClientApproval.agency_client_id == client_id)
        .where(ClientApproval.status == "pending")
    )
    pending_approvals = approvals_result.scalar() or 0
    
    return {
        "id": str(client.id),
        "client_name": client.client_name,
        "client_organization_id": str(client.client_organization_id),
        "primary_contact_name": client.primary_contact_name,
        "primary_contact_email": client.primary_contact_email,
        "monthly_retainer": client.monthly_retainer,
        "status": client.status,
        "contract_start_date": client.contract_start_date.isoformat() if client.contract_start_date else None,
        "contract_end_date": client.contract_end_date.isoformat() if client.contract_end_date else None,
        "internal_notes": client.internal_notes,
        "pending_approvals": pending_approvals,
    }


# === White Label ===

@router.get("/white-label")
async def get_white_label(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get white-label configuration."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(WhiteLabelConfig).where(WhiteLabelConfig.organization_id == org_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        return {"config": None}
    
    return {
        "config": {
            "brand_name": config.brand_name,
            "logo_url": config.logo_url,
            "logo_dark_url": config.logo_dark_url,
            "primary_color": config.primary_color,
            "secondary_color": config.secondary_color,
            "custom_domain": config.custom_domain,
            "hide_powered_by": config.hide_powered_by,
            "is_active": config.is_active,
        }
    }


@router.put("/white-label")
async def update_white_label(
    update: WhiteLabelUpdate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update white-label configuration."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(WhiteLabelConfig).where(WhiteLabelConfig.organization_id == org_id)
    )
    config = result.scalar_one_or_none()
    
    if not config:
        config = WhiteLabelConfig(organization_id=org_id)
        db.add(config)
    
    # Apply updates
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(config, key, value)
    
    config.is_active = True
    await db.commit()
    
    return {"message": "White-label configuration updated"}


# === Approvals ===

@router.get("/clients/{client_id}/approvals")
async def list_approvals(
    client_id: UUID,
    status: Optional[str] = None,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List client approvals."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(ClientApproval).where(ClientApproval.agency_client_id == client_id)
    
    if status:
        query = query.where(ClientApproval.status == status)
    
    query = query.order_by(ClientApproval.requested_at.desc())
    
    result = await db.execute(query)
    approvals = result.scalars().all()
    
    return {
        "approvals": [
            {
                "id": str(a.id),
                "item_type": a.item_type,
                "item_title": a.item_title,
                "status": a.status,
                "requested_at": a.requested_at.isoformat(),
                "responded_at": a.responded_at.isoformat() if a.responded_at else None,
            }
            for a in approvals
        ]
    }


@router.post("/clients/{client_id}/approvals")
async def request_approval(
    client_id: UUID,
    request: ApprovalRequest,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request client approval."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_approval = ClientApproval(
        agency_client_id=client_id,
        item_type=request.item_type,
        item_id=request.item_id,
        item_title=request.item_title,
        requested_by=current_user.id,
        message=request.message,
    )
    db.add(new_approval)
    await db.commit()
    await db.refresh(new_approval)
    
    return {"id": str(new_approval.id), "message": "Approval requested"}


# === Reports ===

@router.get("/clients/{client_id}/reports")
async def list_client_reports(
    client_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List client reports."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ClientReport)
        .where(ClientReport.agency_client_id == client_id)
        .order_by(ClientReport.created_at.desc())
    )
    reports = result.scalars().all()
    
    return {
        "reports": [
            {
                "id": str(r.id),
                "title": r.title,
                "report_type": r.report_type,
                "period_start": r.period_start.isoformat(),
                "period_end": r.period_end.isoformat(),
                "status": r.status,
                "file_url": r.file_url,
                "sent_at": r.sent_at.isoformat() if r.sent_at else None,
            }
            for r in reports
        ]
    }

