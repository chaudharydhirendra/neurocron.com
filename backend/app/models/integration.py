"""
NeuroCron Integration Models
Stores OAuth tokens and platform connections securely
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, DateTime, Boolean, ForeignKey, 
    Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from cryptography.fernet import Fernet
import uuid
import enum
import os

from app.models.base import Base
from app.core.config import settings


class PlatformType(str, enum.Enum):
    """Supported platform types."""
    # Advertising
    GOOGLE_ADS = "google_ads"
    META_ADS = "meta_ads"
    LINKEDIN_ADS = "linkedin_ads"
    TIKTOK_ADS = "tiktok_ads"
    TWITTER_ADS = "twitter_ads"
    
    # Social Media
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    
    # Analytics
    GOOGLE_ANALYTICS = "google_analytics"
    
    # E-commerce
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    
    # CRM
    HUBSPOT = "hubspot"
    SALESFORCE = "salesforce"
    
    # Email
    MAILCHIMP = "mailchimp"
    SENDGRID = "sendgrid"


class IntegrationStatus(str, enum.Enum):
    """Integration connection status."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"
    PENDING = "pending"


class IntegrationToken(Base):
    """
    Stores OAuth tokens for platform integrations.
    Tokens are encrypted at rest using Fernet symmetric encryption.
    """
    __tablename__ = "integration_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    
    # Platform identification
    platform: Mapped[str] = mapped_column(
        SQLEnum(PlatformType), nullable=False
    )
    platform_account_id: Mapped[Optional[str]] = mapped_column(String(255))
    platform_account_name: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Status
    status: Mapped[str] = mapped_column(
        SQLEnum(IntegrationStatus), default=IntegrationStatus.PENDING
    )
    
    # Encrypted tokens (stored as encrypted strings)
    access_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(Text)
    
    # Token metadata
    token_type: Mapped[str] = mapped_column(String(50), default="Bearer")
    scopes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Additional platform-specific data
    platform_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Connection metadata
    connected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    connected_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL")
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    error_count: Mapped[int] = mapped_column(default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    organization = relationship("Organization", back_populates="integrations")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'platform', name='uq_org_platform'),
        Index('ix_integration_org_status', 'organization_id', 'status'),
        Index('ix_integration_expires', 'expires_at'),
    )
    
    # Encryption key derived from SECRET_KEY
    @staticmethod
    def _get_cipher():
        """Get Fernet cipher for encryption/decryption."""
        # Derive a 32-byte key from SECRET_KEY
        import hashlib
        import base64
        key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(key))
    
    def set_access_token(self, token: str):
        """Encrypt and store access token."""
        cipher = self._get_cipher()
        self.access_token_encrypted = cipher.encrypt(token.encode()).decode()
    
    def get_access_token(self) -> Optional[str]:
        """Decrypt and return access token."""
        if not self.access_token_encrypted:
            return None
        cipher = self._get_cipher()
        return cipher.decrypt(self.access_token_encrypted.encode()).decode()
    
    def set_refresh_token(self, token: str):
        """Encrypt and store refresh token."""
        cipher = self._get_cipher()
        self.refresh_token_encrypted = cipher.encrypt(token.encode()).decode()
    
    def get_refresh_token(self) -> Optional[str]:
        """Decrypt and return refresh token."""
        if not self.refresh_token_encrypted:
            return None
        cipher = self._get_cipher()
        return cipher.decrypt(self.refresh_token_encrypted.encode()).decode()
    
    @property
    def is_expired(self) -> bool:
        """Check if access token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() >= self.expires_at
    
    @property
    def needs_refresh(self) -> bool:
        """Check if token needs refresh (expires within 5 minutes)."""
        if not self.expires_at:
            return False
        from datetime import timedelta
        return datetime.utcnow() >= (self.expires_at - timedelta(minutes=5))


class OAuthState(Base):
    """
    Temporary storage for OAuth state during authorization flow.
    Entries are cleaned up after use or expiration.
    """
    __tablename__ = "oauth_states"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    state: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    platform: Mapped[str] = mapped_column(SQLEnum(PlatformType), nullable=False)
    redirect_uri: Mapped[str] = mapped_column(String(500))
    scopes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # PKCE support
    code_verifier: Mapped[Optional[str]] = mapped_column(String(255))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(default=False)
    
    __table_args__ = (
        Index('ix_oauth_state_expires', 'expires_at'),
    )


class PlatformWebhook(Base):
    """
    Stores webhook configurations for platforms.
    """
    __tablename__ = "platform_webhooks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    
    platform: Mapped[str] = mapped_column(SQLEnum(PlatformType), nullable=False)
    webhook_id: Mapped[Optional[str]] = mapped_column(String(255))
    webhook_url: Mapped[str] = mapped_column(String(500))
    secret: Mapped[Optional[str]] = mapped_column(Text)  # Encrypted
    
    events: Mapped[Optional[List[str]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    last_received_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

