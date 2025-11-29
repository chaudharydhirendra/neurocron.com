"""
NeuroCron Organizations API
Organization and workspace management
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re

from app.core.deps import get_db, get_current_user
from app.models.organization import Organization, OrganizationMember
from app.models.user import UserRole
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)

router = APIRouter()


def generate_slug(name: str) -> str:
    """Generate URL-safe slug from name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_in: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new organization.
    
    The creating user becomes the owner automatically.
    """
    # Generate slug if not provided
    slug = org_in.slug or generate_slug(org_in.name)
    
    # Check if slug already exists
    result = await db.execute(
        select(Organization).where(Organization.slug == slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists"
        )
    
    # Create organization
    org = Organization(
        name=org_in.name,
        slug=slug,
        description=org_in.description,
        website=org_in.website,
        industry=org_in.industry,
        company_size=org_in.company_size,
    )
    db.add(org)
    await db.flush()
    
    # Add creator as owner
    member = OrganizationMember(
        organization_id=org.id,
        user_id=UUID(current_user["id"]),
        role=UserRole.OWNER,
    )
    db.add(member)
    
    await db.commit()
    await db.refresh(org)
    
    return org


@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all organizations the current user is a member of.
    """
    result = await db.execute(
        select(Organization)
        .join(OrganizationMember)
        .where(OrganizationMember.user_id == UUID(current_user["id"]))
        .where(OrganizationMember.is_active == True)
    )
    organizations = result.scalars().all()
    return organizations


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get organization details.
    
    User must be a member of the organization.
    """
    # Verify user is a member
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == UUID(current_user["id"]))
        .where(OrganizationMember.is_active == True)
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_in: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update organization details.
    
    Requires admin or owner role.
    """
    # Verify user has permission
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == UUID(current_user["id"]))
        .where(OrganizationMember.role.in_([UserRole.OWNER, UserRole.ADMIN]))
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Get and update organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Update fields
    update_data = org_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    
    await db.commit()
    await db.refresh(org)
    
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an organization.
    
    Requires owner role.
    """
    # Verify user is owner
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == UUID(current_user["id"]))
        .where(OrganizationMember.role == UserRole.OWNER)
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can delete"
        )
    
    # Delete organization (cascade will handle members)
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if org:
        await db.delete(org)
        await db.commit()
    
    return None

