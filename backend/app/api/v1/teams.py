"""
NeuroCron Team Management API
Team invitations, roles, and permissions
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

router = APIRouter()


class TeamMemberResponse(BaseModel):
    id: str
    user_id: str
    email: str
    full_name: str
    role: str
    joined_at: str
    is_active: bool


class InviteCreate(BaseModel):
    email: EmailStr
    role: str = "member"  # owner, admin, member, viewer


class InviteResponse(BaseModel):
    id: str
    email: str
    role: str
    status: str
    expires_at: str
    created_at: str


class RoleUpdate(BaseModel):
    role: str


# Role hierarchy for permission checks
ROLE_HIERARCHY = {
    "owner": 4,
    "admin": 3,
    "member": 2,
    "viewer": 1,
}

ROLE_PERMISSIONS = {
    "owner": ["*"],  # All permissions
    "admin": [
        "manage_team", "manage_campaigns", "manage_content", 
        "manage_integrations", "view_analytics", "manage_flows",
        "manage_billing"
    ],
    "member": [
        "manage_campaigns", "manage_content", "view_analytics", 
        "manage_flows", "use_copilot"
    ],
    "viewer": ["view_analytics", "view_campaigns", "view_content"],
}


def check_permission(user_role: str, target_role: str) -> bool:
    """Check if user can manage target role"""
    return ROLE_HIERARCHY.get(user_role, 0) > ROLE_HIERARCHY.get(target_role, 0)


@router.get("/members")
async def list_team_members(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all team members in an organization."""
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
    
    # Fetch all members with user info
    result = await db.execute(
        select(OrganizationMember, User)
        .join(User, OrganizationMember.user_id == User.id)
        .where(OrganizationMember.organization_id == org_id)
        .order_by(OrganizationMember.created_at)
    )
    rows = result.all()
    
    return {
        "members": [
            {
                "id": str(member.id),
                "user_id": str(member.user_id),
                "email": user.email,
                "full_name": user.full_name,
                "role": member.role,
                "joined_at": member.created_at.isoformat() if member.created_at else None,
                "is_active": user.is_active,
            }
            for member, user in rows
        ],
        "total": len(rows),
    }


@router.post("/invite")
async def invite_member(
    invite: InviteCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invite a new team member."""
    # Verify admin/owner permissions
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to invite members"
        )
    
    # Check if inviting a role higher than own
    if not check_permission(member.role, invite.role) and member.role != "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot invite member with equal or higher role"
        )
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == invite.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Check if already a member
        result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.organization_id == org_id)
            .where(OrganizationMember.user_id == existing_user.id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this organization"
            )
        
        # Add directly to organization
        new_member = OrganizationMember(
            organization_id=org_id,
            user_id=existing_user.id,
            role=invite.role,
        )
        db.add(new_member)
        await db.commit()
        
        return {
            "message": f"User {invite.email} added to the organization",
            "status": "added",
        }
    
    # Create invitation token (in production, store in a pending_invites table)
    invite_token = secrets.token_urlsafe(32)
    
    # In production, send email with invite link
    # For now, return the invite details
    return {
        "message": f"Invitation sent to {invite.email}",
        "status": "pending",
        "invite_token": invite_token,  # In production, don't expose this
        "invite_url": f"https://neurocron.com/invite/{invite_token}",
        "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat(),
    }


@router.put("/members/{member_id}/role")
async def update_member_role(
    member_id: UUID,
    role_update: RoleUpdate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a team member's role."""
    # Verify admin/owner permissions
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    current_member = result.scalar_one_or_none()
    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to update roles"
        )
    
    # Get target member
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.id == member_id)
        .where(OrganizationMember.organization_id == org_id)
    )
    target_member = result.scalar_one_or_none()
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Can't change owner's role
    if target_member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change owner's role"
        )
    
    # Can't set role higher than own (unless owner)
    if current_member.role != "owner" and not check_permission(current_member.role, role_update.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot assign role equal to or higher than your own"
        )
    
    target_member.role = role_update.role
    await db.commit()
    
    return {"message": "Role updated successfully", "new_role": role_update.role}


@router.delete("/members/{member_id}")
async def remove_member(
    member_id: UUID,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a team member from the organization."""
    # Verify admin/owner permissions
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    current_member = result.scalar_one_or_none()
    if not current_member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to remove members"
        )
    
    # Get target member
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.id == member_id)
        .where(OrganizationMember.organization_id == org_id)
    )
    target_member = result.scalar_one_or_none()
    if not target_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    # Can't remove owner
    if target_member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot remove the organization owner"
        )
    
    # Can't remove self (use leave instead)
    if target_member.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove yourself. Use leave organization instead."
        )
    
    # Admin can't remove other admins
    if current_member.role == "admin" and target_member.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins cannot remove other admins"
        )
    
    await db.delete(target_member)
    await db.commit()
    
    return {"message": "Member removed successfully"}


@router.post("/leave")
async def leave_organization(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave an organization."""
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not a member of this organization"
        )
    
    # Owner can't leave (must transfer ownership first)
    if member.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner cannot leave. Transfer ownership first."
        )
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "You have left the organization"}


@router.post("/transfer-ownership")
async def transfer_ownership(
    new_owner_id: UUID,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Transfer organization ownership to another member."""
    # Verify current user is owner
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role == "owner")
    )
    current_owner = result.scalar_one_or_none()
    if not current_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can transfer ownership"
        )
    
    # Get new owner
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == new_owner_id)
    )
    new_owner = result.scalar_one_or_none()
    if not new_owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New owner must be an existing member"
        )
    
    # Transfer ownership
    current_owner.role = "admin"
    new_owner.role = "owner"
    await db.commit()
    
    return {"message": "Ownership transferred successfully"}


@router.get("/permissions")
async def get_my_permissions(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's permissions in the organization."""
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organization"
        )
    
    return {
        "role": member.role,
        "permissions": ROLE_PERMISSIONS.get(member.role, []),
        "can_manage_team": member.role in ["owner", "admin"],
        "can_manage_billing": member.role in ["owner", "admin"],
        "is_owner": member.role == "owner",
    }

