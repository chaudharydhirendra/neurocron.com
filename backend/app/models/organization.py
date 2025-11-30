"""
NeuroCron Organization Model
Multi-tenant organization and workspace management
"""

import uuid
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base
from app.models.user import UserRole


class PlanType(str, enum.Enum):
    """Subscription plan types"""
    FREE = "free"
    STARTER = "starter"
    GROWTH = "growth"
    ENTERPRISE = "enterprise"


class Organization(Base):
    """Organization model for multi-tenancy"""
    
    __tablename__ = "organizations"
    
    # Basic info
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    
    # Business info
    industry: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    company_size: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    
    # Subscription
    plan: Mapped[PlanType] = mapped_column(
        SQLEnum(PlanType),
        default=PlanType.FREE,
        nullable=False,
    )
    
    # Settings (JSON)
    settings: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        default=dict,
        nullable=True,
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        lazy="selectin",
    )
    campaigns: Mapped[List["Campaign"]] = relationship(
        "Campaign",
        back_populates="organization",
        lazy="selectin",
    )
    integrations: Mapped[List["IntegrationToken"]] = relationship(
        "IntegrationToken",
        back_populates="organization",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<Organization {self.name}>"


class OrganizationMember(Base):
    """Organization membership - links users to organizations with roles"""
    
    __tablename__ = "organization_members"
    
    # Foreign keys
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Role
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.MEMBER,
        nullable=False,
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates="organizations",
    )
    
    def __repr__(self) -> str:
        return f"<OrganizationMember {self.user_id} in {self.organization_id}>"

