"""
NeuroCron GlobalReach Models
Multi-language content localization
"""

import uuid
from typing import Optional, List
from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TranslationProject(Base):
    """
    Translation project for content localization.
    """
    
    __tablename__ = "translation_projects"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Project info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source language
    source_language: Mapped[str] = mapped_column(String(10), default="en")
    
    # Target languages (JSON array)
    target_languages: Mapped[dict] = mapped_column(JSONB, default=list)
    
    # Content type
    content_type: Mapped[str] = mapped_column(String(50), default="marketing")
    # Types: marketing, website, email, ad, social, document
    
    # Stats
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    translated_items: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, in_progress, review, completed


class TranslationItem(Base):
    """
    Individual content item for translation.
    """
    
    __tablename__ = "translation_items"
    
    # Project
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("translation_projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Item info
    item_key: Mapped[str] = mapped_column(String(255), nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), default="text")  # text, html, markdown
    context: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Source content
    source_content: Mapped[str] = mapped_column(Text, nullable=False)
    source_language: Mapped[str] = mapped_column(String(10), default="en")
    
    # Character count
    char_count: Mapped[int] = mapped_column(Integer, default=0)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Tags
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, default=list)
    
    __table_args__ = (
        Index("ix_translation_items_project_key", "project_id", "item_key"),
    )


class Translation(Base):
    """
    Translated version of an item.
    """
    
    __tablename__ = "translations"
    
    # Item
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("translation_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Target language
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Translation
    translated_content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Translation method
    translation_method: Mapped[str] = mapped_column(String(20), default="ai")  # ai, human, hybrid
    
    # Quality
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-100
    
    # Review status
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Approval
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (
        Index("ix_translations_item_lang", "item_id", "target_language", unique=True),
    )


class LocaleSettings(Base):
    """
    Organization locale/region settings.
    """
    
    __tablename__ = "locale_settings"
    
    # Organization
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Locale
    locale_code: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., en-US, fr-FR
    language_code: Mapped[str] = mapped_column(String(5), nullable=False)  # e.g., en, fr
    region_code: Mapped[Optional[str]] = mapped_column(String(5), nullable=True)  # e.g., US, FR
    
    # Display name
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    native_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Formatting
    date_format: Mapped[str] = mapped_column(String(50), default="MM/DD/YYYY")
    time_format: Mapped[str] = mapped_column(String(50), default="12h")
    currency_code: Mapped[str] = mapped_column(String(3), default="USD")
    number_format: Mapped[str] = mapped_column(String(20), default="1,234.56")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    
    __table_args__ = (
        Index("ix_locale_settings_org_locale", "organization_id", "locale_code", unique=True),
    )

