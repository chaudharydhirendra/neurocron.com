"""
NeuroCron Integrations API
OAuth connections for marketing platforms with secure token storage
"""

from typing import List, Optional
from uuid import UUID
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
import httpx

from app.core.deps import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.integration import (
    IntegrationToken, OAuthState, PlatformType, IntegrationStatus
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# Platform Configuration
# ═══════════════════════════════════════════════════════════════════

PLATFORM_CONFIG = {
    PlatformType.GOOGLE_ADS: {
        "name": "Google Ads",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/adwords",
        ],
        "client_id_env": "GOOGLE_CLIENT_ID",
        "client_secret_env": "GOOGLE_CLIENT_SECRET",
    },
    PlatformType.GOOGLE_ANALYTICS: {
        "name": "Google Analytics",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/analytics.readonly",
        ],
        "client_id_env": "GOOGLE_CLIENT_ID",
        "client_secret_env": "GOOGLE_CLIENT_SECRET",
    },
    PlatformType.META_ADS: {
        "name": "Meta Ads (Facebook/Instagram)",
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": [
            "ads_management",
            "ads_read",
            "pages_read_engagement",
            "instagram_basic",
        ],
        "client_id_env": "META_APP_ID",
        "client_secret_env": "META_APP_SECRET",
    },
    PlatformType.LINKEDIN_ADS: {
        "name": "LinkedIn Ads",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": [
            "r_ads",
            "r_ads_reporting",
            "rw_ads",
        ],
        "client_id_env": "LINKEDIN_CLIENT_ID",
        "client_secret_env": "LINKEDIN_CLIENT_SECRET",
    },
    PlatformType.TWITTER: {
        "name": "Twitter/X",
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scopes": [
            "tweet.read",
            "tweet.write",
            "users.read",
        ],
        "client_id_env": "TWITTER_CLIENT_ID",
        "client_secret_env": "TWITTER_CLIENT_SECRET",
        "pkce": True,  # Twitter requires PKCE
    },
    PlatformType.HUBSPOT: {
        "name": "HubSpot",
        "auth_url": "https://app.hubspot.com/oauth/authorize",
        "token_url": "https://api.hubapi.com/oauth/v1/token",
        "scopes": [
            "crm.objects.contacts.read",
            "crm.objects.contacts.write",
            "crm.objects.deals.read",
        ],
        "client_id_env": "HUBSPOT_CLIENT_ID",
        "client_secret_env": "HUBSPOT_CLIENT_SECRET",
    },
}


# ═══════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════

class IntegrationResponse(BaseModel):
    """Integration response schema."""
    id: str
    platform: str
    platform_name: str
    status: str
    connected_at: Optional[str] = None
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    scopes: Optional[List[str]] = None
    expires_at: Optional[str] = None
    last_error: Optional[str] = None


class ConnectRequest(BaseModel):
    """Request to initiate OAuth connection."""
    platform: str = Field(..., description="Platform type")


class DisconnectRequest(BaseModel):
    """Request to disconnect an integration."""
    platform: str


# ═══════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════

def get_platform_credentials(platform: PlatformType) -> tuple[str, str]:
    """Get OAuth credentials for a platform from environment."""
    import os
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        raise ValueError(f"Unknown platform: {platform}")
    
    client_id = os.getenv(config["client_id_env"], "")
    client_secret = os.getenv(config["client_secret_env"], "")
    
    return client_id, client_secret


def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge."""
    code_verifier = secrets.token_urlsafe(64)[:128]
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode().rstrip("=")
    return code_verifier, code_challenge


async def cleanup_expired_states(db: AsyncSession):
    """Clean up expired OAuth states."""
    await db.execute(
        delete(OAuthState).where(OAuthState.expires_at < datetime.utcnow())
    )
    await db.commit()


# ═══════════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════════

@router.get("/", response_model=List[IntegrationResponse])
async def list_integrations(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all integrations for an organization.
    Shows connected platforms and available ones to connect.
    """
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
    
    # Fetch existing integrations
    result = await db.execute(
        select(IntegrationToken)
        .where(IntegrationToken.organization_id == org_id)
    )
    existing = {t.platform: t for t in result.scalars().all()}
    
    integrations = []
    for platform, config in PLATFORM_CONFIG.items():
        token = existing.get(platform)
        
        if token:
            integrations.append(IntegrationResponse(
                id=str(token.id),
                platform=platform.value,
                platform_name=config["name"],
                status=token.status.value,
                connected_at=token.connected_at.isoformat() if token.connected_at else None,
                account_id=token.platform_account_id,
                account_name=token.platform_account_name,
                scopes=token.scopes,
                expires_at=token.expires_at.isoformat() if token.expires_at else None,
                last_error=token.last_error,
            ))
        else:
            # Check if credentials are configured
            client_id, _ = get_platform_credentials(platform)
            integrations.append(IntegrationResponse(
                id=f"new-{platform.value}",
                platform=platform.value,
                platform_name=config["name"],
                status="available" if client_id else "not_configured",
                scopes=config["scopes"],
            ))
    
    return integrations


@router.post("/connect")
async def initiate_connection(
    request: ConnectRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate OAuth connection to a platform.
    Returns the authorization URL to redirect the user to.
    """
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
    
    # Parse platform
    try:
        platform = PlatformType(request.platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {request.platform}"
        )
    
    config = PLATFORM_CONFIG.get(platform)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform not supported: {platform}"
        )
    
    # Get credentials
    client_id, client_secret = get_platform_credentials(platform)
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform credentials not configured. Set {config['client_id_env']} and {config['client_secret_env']} environment variables."
        )
    
    # Clean up old states
    await cleanup_expired_states(db)
    
    # Generate state and PKCE
    state = secrets.token_urlsafe(32)
    code_verifier = None
    code_challenge = None
    
    if config.get("pkce"):
        code_verifier, code_challenge = generate_pkce_pair()
    
    redirect_uri = f"{settings.API_URL}/api/v1/integrations/callback/{platform.value}"
    
    # Store state in database
    oauth_state = OAuthState(
        state=state,
        organization_id=org_id,
        user_id=current_user.id,
        platform=platform,
        redirect_uri=redirect_uri,
        scopes=config["scopes"],
        code_verifier=code_verifier,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.add(oauth_state)
    await db.commit()
    
    # Build authorization URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(config["scopes"]),
        "state": state,
        "access_type": "offline",  # For refresh tokens
        "prompt": "consent",  # Always show consent to get refresh token
    }
    
    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"
    
    auth_url = f"{config['auth_url']}?{urlencode(params)}"
    
    return {
        "authorization_url": auth_url,
        "state": state,
        "expires_in": 600,  # 10 minutes
    }


@router.get("/callback/{platform}")
async def oauth_callback(
    platform: str,
    code: str = Query(...),
    state: str = Query(...),
    error: Optional[str] = Query(None),
    error_description: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth callback handler.
    Exchanges authorization code for access token and stores it securely.
    """
    # Handle errors from OAuth provider
    if error:
        logger.error(f"OAuth error for {platform}: {error} - {error_description}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/settings?tab=integrations&error={error}"
        )
    
    # Validate state
    result = await db.execute(
        select(OAuthState)
        .where(OAuthState.state == state)
        .where(OAuthState.used == False)
        .where(OAuthState.expires_at > datetime.utcnow())
    )
    oauth_state = result.scalar_one_or_none()
    
    if not oauth_state:
        logger.error(f"Invalid or expired OAuth state for {platform}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/settings?tab=integrations&error=invalid_state"
        )
    
    # Mark state as used
    oauth_state.used = True
    
    try:
        platform_type = PlatformType(platform)
    except ValueError:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/settings?tab=integrations&error=unknown_platform"
        )
    
    config = PLATFORM_CONFIG.get(platform_type)
    client_id, client_secret = get_platform_credentials(platform_type)
    
    # Exchange code for tokens
    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": oauth_state.redirect_uri,
        "grant_type": "authorization_code",
    }
    
    if oauth_state.code_verifier:
        token_data["code_verifier"] = oauth_state.code_verifier
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/settings?tab=integrations&error=token_exchange_failed"
                )
            
            tokens = response.json()
    except Exception as e:
        logger.error(f"Token exchange error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/settings?tab=integrations&error=connection_failed"
        )
    
    # Check for existing integration
    result = await db.execute(
        select(IntegrationToken)
        .where(IntegrationToken.organization_id == oauth_state.organization_id)
        .where(IntegrationToken.platform == platform_type)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        integration = IntegrationToken(
            organization_id=oauth_state.organization_id,
            platform=platform_type,
            connected_by=oauth_state.user_id,
        )
        db.add(integration)
    
    # Store tokens securely
    integration.set_access_token(tokens.get("access_token", ""))
    if tokens.get("refresh_token"):
        integration.set_refresh_token(tokens.get("refresh_token"))
    
    integration.token_type = tokens.get("token_type", "Bearer")
    integration.scopes = oauth_state.scopes
    integration.status = IntegrationStatus.CONNECTED
    integration.connected_at = datetime.utcnow()
    integration.last_refresh_at = datetime.utcnow()
    integration.error_count = 0
    integration.last_error = None
    
    # Calculate expiration
    expires_in = tokens.get("expires_in")
    if expires_in:
        integration.expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
    
    # Try to get account info
    account_info = await _get_account_info(platform_type, tokens.get("access_token", ""))
    if account_info:
        integration.platform_account_id = account_info.get("id")
        integration.platform_account_name = account_info.get("name")
    
    await db.commit()
    
    logger.info(f"Successfully connected {platform} for org {oauth_state.organization_id}")
    
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/settings?tab=integrations&success={platform}"
    )


async def _get_account_info(platform: PlatformType, access_token: str) -> Optional[dict]:
    """Fetch account info from the platform API."""
    try:
        async with httpx.AsyncClient() as client:
            if platform in [PlatformType.GOOGLE_ADS, PlatformType.GOOGLE_ANALYTICS]:
                # Google user info
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {"id": data.get("id"), "name": data.get("email")}
            
            elif platform == PlatformType.META_ADS:
                response = await client.get(
                    "https://graph.facebook.com/v18.0/me",
                    params={"access_token": access_token, "fields": "id,name"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
            
            elif platform == PlatformType.LINKEDIN_ADS:
                response = await client.get(
                    "https://api.linkedin.com/v2/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "id": data.get("id"),
                        "name": f"{data.get('localizedFirstName', '')} {data.get('localizedLastName', '')}".strip()
                    }
    except Exception as e:
        logger.error(f"Failed to get account info for {platform}: {e}")
    
    return None


@router.post("/disconnect")
async def disconnect_integration(
    request: DisconnectRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Disconnect an integration."""
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
    
    try:
        platform = PlatformType(request.platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {request.platform}"
        )
    
    # Find and delete integration
    result = await db.execute(
        select(IntegrationToken)
        .where(IntegrationToken.organization_id == org_id)
        .where(IntegrationToken.platform == platform)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    await db.delete(integration)
    await db.commit()
    
    logger.info(f"Disconnected {platform} for org {org_id}")
    
    return {"message": f"Successfully disconnected {platform.value}"}


@router.post("/refresh/{platform}")
async def refresh_token(
    platform: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually refresh an integration's access token."""
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
    
    try:
        platform_type = PlatformType(platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {platform}"
        )
    
    result = await db.execute(
        select(IntegrationToken)
        .where(IntegrationToken.organization_id == org_id)
        .where(IntegrationToken.platform == platform_type)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    refresh_token = integration.get_refresh_token()
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token available. Please reconnect the integration."
        )
    
    config = PLATFORM_CONFIG.get(platform_type)
    client_id, client_secret = get_platform_credentials(platform_type)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                config["token_url"],
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Accept": "application/json"},
                timeout=30.0,
            )
            
            if response.status_code != 200:
                integration.status = IntegrationStatus.ERROR
                integration.last_error = f"Token refresh failed: {response.text}"
                integration.error_count += 1
                await db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token refresh failed"
                )
            
            tokens = response.json()
    except httpx.RequestError as e:
        integration.status = IntegrationStatus.ERROR
        integration.last_error = str(e)
        integration.error_count += 1
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to platform"
        )
    
    # Update tokens
    integration.set_access_token(tokens.get("access_token", ""))
    if tokens.get("refresh_token"):
        integration.set_refresh_token(tokens.get("refresh_token"))
    
    integration.status = IntegrationStatus.CONNECTED
    integration.last_refresh_at = datetime.utcnow()
    integration.error_count = 0
    integration.last_error = None
    
    expires_in = tokens.get("expires_in")
    if expires_in:
        integration.expires_at = datetime.utcnow() + timedelta(seconds=int(expires_in))
    
    await db.commit()
    
    return {
        "message": "Token refreshed successfully",
        "expires_at": integration.expires_at.isoformat() if integration.expires_at else None,
    }


@router.get("/status/{platform}")
async def get_integration_status(
    platform: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed status of a specific integration."""
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
    
    try:
        platform_type = PlatformType(platform)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {platform}"
        )
    
    result = await db.execute(
        select(IntegrationToken)
        .where(IntegrationToken.organization_id == org_id)
        .where(IntegrationToken.platform == platform_type)
    )
    integration = result.scalar_one_or_none()
    
    if not integration:
        return {
            "connected": False,
            "status": "disconnected",
            "platform": platform,
        }
    
    return {
        "connected": integration.status == IntegrationStatus.CONNECTED,
        "status": integration.status.value,
        "platform": platform,
        "account_id": integration.platform_account_id,
        "account_name": integration.platform_account_name,
        "scopes": integration.scopes,
        "connected_at": integration.connected_at.isoformat() if integration.connected_at else None,
        "expires_at": integration.expires_at.isoformat() if integration.expires_at else None,
        "is_expired": integration.is_expired,
        "needs_refresh": integration.needs_refresh,
        "last_used_at": integration.last_used_at.isoformat() if integration.last_used_at else None,
        "last_error": integration.last_error,
        "error_count": integration.error_count,
    }
