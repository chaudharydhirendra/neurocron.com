"""
NeuroCron Organization Schemas
Pydantic models for organization-related requests/responses
"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl

from app.models.organization import PlanType
from app.models.user import UserRole


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    slug: Optional[str] = Field(None, min_length=3, max_length=100, pattern="^[a-z0-9-]+$")


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    settings: Optional[dict] = None


class OrganizationMemberResponse(BaseModel):
    """Organization member response"""
    id: UUID
    user_id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: UUID
    slug: str
    logo_url: Optional[str] = None
    plan: PlanType
    is_active: bool
    created_at: datetime
    updated_at: datetime
    members: Optional[List[OrganizationMemberResponse]] = None
    
    class Config:
        from_attributes = True


class OrganizationInvite(BaseModel):
    """Invite a user to organization"""
    email: str
    role: UserRole = UserRole.MEMBER


class OrganizationMemberUpdate(BaseModel):
    """Update member role"""
    role: UserRole

