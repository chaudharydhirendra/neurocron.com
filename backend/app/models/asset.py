"""
NeuroCron BrandVault Models
Asset library with versioning, tagging, and organization
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base


class AssetType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    TEMPLATE = "template"
    LOGO = "logo"
    ICON = "icon"
    FONT = "font"
    OTHER = "other"


class Asset(Base):
    """
    Brand asset (image, video, document, template, etc.)
    """
    
    __tablename__ = "assets"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Uploaded by
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Folder
    folder_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_folders.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Asset info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # File details
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)  # MIME type
    file_size: Mapped[int] = mapped_column(Integer, default=0)  # bytes
    file_extension: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Storage
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # URLs
    public_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cdn_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Type
    asset_type: Mapped[AssetType] = mapped_column(
        Enum(AssetType), default=AssetType.OTHER
    )
    
    # Dimensions (for images/videos)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # seconds for video/audio
    
    # File metadata
    file_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    exif_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # AI-generated
    alt_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    ai_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=True)
    previous_version_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # Usage tracking
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)  # times used in campaigns
    
    # Status
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    __table_args__ = (
        Index("ix_assets_org_type", "organization_id", "asset_type"),
        Index("ix_assets_org_folder", "organization_id", "folder_id"),
    )


class AssetFolder(Base):
    """
    Folder for organizing assets.
    """
    
    __tablename__ = "asset_folders"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Parent folder (for nesting)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_folders.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Folder info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Path (for faster lookups)
    path: Mapped[str] = mapped_column(String(1000), default="/")
    depth: Mapped[int] = mapped_column(Integer, default=0)
    
    # Counts
    asset_count: Mapped[int] = mapped_column(Integer, default=0)
    subfolder_count: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_folders_org_parent", "organization_id", "parent_id"),
    )


class AssetTag(Base):
    """
    Tag for categorizing assets.
    """
    
    __tablename__ = "asset_tags"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Tag info
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Usage
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_asset_tags_org_name", "organization_id", "name", unique=True),
    )


class AssetTagMapping(Base):
    """
    Many-to-many relationship between assets and tags.
    """
    
    __tablename__ = "asset_tag_mappings"
    
    asset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    tag_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("asset_tags.id", ondelete="CASCADE"),
        primary_key=True,
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BrandGuideline(Base):
    """
    Brand guidelines and style guide.
    """
    
    __tablename__ = "brand_guidelines"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    
    # Brand info
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    mission: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    voice_tone: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Colors (JSON array)
    primary_colors: Mapped[dict] = mapped_column(JSONB, default=list)
    secondary_colors: Mapped[dict] = mapped_column(JSONB, default=list)
    
    # Typography
    primary_font: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    secondary_font: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    font_guidelines: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Logos
    primary_logo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    logo_usage_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Additional guidelines
    do_guidelines: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    dont_guidelines: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

