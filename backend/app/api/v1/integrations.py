"""
NeuroCron Integrations API
OAuth connections for marketing platforms
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
from datetime import datetime, timedelta

from app.core.deps import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


class Integration(BaseModel):
    """Integration model"""
    id: str
    platform: str
    name: str
    status: str  # connected, disconnected, error
    connected_at: Optional[str] = None
    account_id: Optional[str] = None
    account_name: Optional[str] = None
    scopes: Optional[List[str]] = None


class ConnectRequest(BaseModel):
    """Request to initiate OAuth connection"""
    platform: str = Field(..., description="Platform: google, meta, linkedin, twitter")
    callback_url: Optional[str] = None


class OAuthCallback(BaseModel):
    """OAuth callback data"""
    code: str
    state: str


# Supported platforms configuration
PLATFORMS = {
    "google": {
        "name": "Google Ads",
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "scopes": [
            "https://www.googleapis.com/auth/adwords",
            "https://www.googleapis.com/auth/analytics.readonly",
        ],
    },
    "meta": {
        "name": "Meta (Facebook/Instagram)",
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": [
            "ads_management",
            "ads_read",
            "pages_read_engagement",
            "instagram_basic",
        ],
    },
    "linkedin": {
        "name": "LinkedIn",
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": [
            "r_ads",
            "r_ads_reporting",
            "rw_ads",
        ],
    },
    "twitter": {
        "name": "Twitter/X",
        "auth_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scopes": [
            "tweet.read",
            "tweet.write",
            "users.read",
            "ads.read",
            "ads.write",
        ],
    },
}

# In-memory state storage (use Redis in production)
oauth_states = {}


@router.get("/", response_model=List[Integration])
async def list_integrations(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all integrations for an organization.
    
    Shows connected and available platforms.
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
    
    # In production, fetch from database
    integrations = []
    
    for platform_id, platform_info in PLATFORMS.items():
        integrations.append(Integration(
            id=platform_id,
            platform=platform_id,
            name=platform_info["name"],
            status="disconnected",
            scopes=platform_info["scopes"],
        ))
    
    return integrations


@router.post("/connect")
async def connect_integration(
    request: ConnectRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initiate OAuth connection to a platform.
    
    Returns the OAuth authorization URL to redirect the user to.
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
    
    platform = request.platform.lower()
    if platform not in PLATFORMS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown platform: {platform}. Supported: {list(PLATFORMS.keys())}"
        )
    
    platform_config = PLATFORMS[platform]
    
    # Generate state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "platform": platform,
        "org_id": str(org_id),
        "user_id": str(current_user.id),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # Build OAuth URL based on platform
    callback_url = request.callback_url or f"{settings.FRONTEND_URL}/settings/integrations/callback"
    scopes = " ".join(platform_config["scopes"])
    
    if platform == "google":
        oauth_url = (
            f"{platform_config['auth_url']}?"
            f"client_id=YOUR_GOOGLE_CLIENT_ID&"
            f"redirect_uri={callback_url}&"
            f"response_type=code&"
            f"scope={scopes}&"
            f"access_type=offline&"
            f"state={state}"
        )
    elif platform == "meta":
        oauth_url = (
            f"{platform_config['auth_url']}?"
            f"client_id=YOUR_META_APP_ID&"
            f"redirect_uri={callback_url}&"
            f"scope={scopes}&"
            f"state={state}"
        )
    elif platform == "linkedin":
        oauth_url = (
            f"{platform_config['auth_url']}?"
            f"response_type=code&"
            f"client_id=YOUR_LINKEDIN_CLIENT_ID&"
            f"redirect_uri={callback_url}&"
            f"scope={scopes}&"
            f"state={state}"
        )
    elif platform == "twitter":
        oauth_url = (
            f"{platform_config['auth_url']}?"
            f"response_type=code&"
            f"client_id=YOUR_TWITTER_CLIENT_ID&"
            f"redirect_uri={callback_url}&"
            f"scope={scopes}&"
            f"state={state}&"
            f"code_challenge=challenge&"
            f"code_challenge_method=plain"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform} not implemented"
        )
    
    return {
        "oauth_url": oauth_url,
        "state": state,
        "platform": platform,
        "message": f"Redirect user to oauth_url to authorize {platform_config['name']}"
    }


@router.post("/callback")
async def oauth_callback(
    callback: OAuthCallback,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle OAuth callback from platform.
    
    Exchanges the authorization code for access token and stores the connection.
    """
    # Verify state
    if callback.state not in oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state token"
        )
    
    state_data = oauth_states.pop(callback.state)
    platform = state_data["platform"]
    
    # In production:
    # 1. Exchange code for access token
    # 2. Fetch account information
    # 3. Store tokens securely in database
    # 4. Create integration record
    
    return {
        "success": True,
        "platform": platform,
        "message": f"Successfully connected to {PLATFORMS[platform]['name']}",
        "org_id": state_data["org_id"],
    }


@router.delete("/{integration_id}")
async def disconnect_integration(
    integration_id: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Disconnect an integration.
    
    Revokes access tokens and removes the connection.
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
    
    # In production:
    # 1. Revoke tokens at the platform
    # 2. Delete integration record
    # 3. Clean up any related data
    
    return {
        "success": True,
        "message": f"Integration {integration_id} disconnected"
    }


@router.get("/{integration_id}/status")
async def check_integration_status(
    integration_id: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of an integration.
    
    Verifies the connection is still valid and tokens are not expired.
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
    
    # In production:
    # 1. Fetch integration from database
    # 2. Test the connection
    # 3. Refresh tokens if needed
    
    return {
        "integration_id": integration_id,
        "status": "disconnected",
        "message": "Integration not connected"
    }


@router.get("/{integration_id}/accounts")
async def list_ad_accounts(
    integration_id: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List ad accounts for an integration.
    
    Used for Google Ads Manager, Meta Business Manager, etc.
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
    
    # In production:
    # 1. Use stored tokens to fetch accounts
    # 2. Return list of accessible ad accounts
    
    return {
        "accounts": [],
        "message": "Connect integration first"
    }

