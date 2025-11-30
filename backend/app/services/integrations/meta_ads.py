"""
Meta (Facebook/Instagram) Marketing API Integration
Manage Meta ads campaigns from NeuroCron
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel


class MetaAdsConfig:
    """Meta Marketing API configuration"""
    APP_ID = os.getenv("META_APP_ID")
    APP_SECRET = os.getenv("META_APP_SECRET")
    REDIRECT_URI = os.getenv("META_REDIRECT_URI", "https://neurocron.com/integrations/meta/callback")
    SCOPES = [
        "ads_management",
        "ads_read",
        "business_management",
        "pages_read_engagement",
        "instagram_basic",
    ]


class MetaAdsCredential(BaseModel):
    """OAuth credentials for Meta Ads"""
    access_token: str
    token_type: str = "bearer"
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    ad_account_id: Optional[str] = None


class MetaAdsService:
    """
    Service for interacting with Meta Marketing API
    
    Features:
    - OAuth authentication
    - Campaign management (CRUD)
    - Ad set management
    - Ad creative management
    - Audience targeting
    - Performance insights
    - Instagram integration
    """
    
    GRAPH_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, credentials: Optional[MetaAdsCredential] = None):
        self.credentials = credentials
        self.config = MetaAdsConfig()
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.config.APP_ID,
            "redirect_uri": self.config.REDIRECT_URI,
            "scope": ",".join(self.config.SCOPES),
            "response_type": "code",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"https://www.facebook.com/v18.0/dialog/oauth?{query}"
    
    async def exchange_code(self, code: str) -> MetaAdsCredential:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GRAPH_URL}/oauth/access_token",
                params={
                    "client_id": self.config.APP_ID,
                    "client_secret": self.config.APP_SECRET,
                    "redirect_uri": self.config.REDIRECT_URI,
                    "code": code,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            # Get long-lived token
            long_lived = await self._get_long_lived_token(data["access_token"])
            
            return MetaAdsCredential(
                access_token=long_lived["access_token"],
                expires_at=datetime.utcnow() + timedelta(seconds=long_lived.get("expires_in", 5184000)),
            )
    
    async def _get_long_lived_token(self, short_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived token."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.GRAPH_URL}/oauth/access_token",
                params={
                    "grant_type": "fb_exchange_token",
                    "client_id": self.config.APP_ID,
                    "client_secret": self.config.APP_SECRET,
                    "fb_exchange_token": short_token,
                },
            )
            response.raise_for_status()
            return response.json()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Meta Graph API."""
        if not self.credentials:
            raise ValueError("No credentials configured")
        
        params = params or {}
        params["access_token"] = self.credentials.access_token
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(
                    f"{self.GRAPH_URL}/{endpoint}",
                    params=params,
                )
            elif method == "POST":
                response = await client.post(
                    f"{self.GRAPH_URL}/{endpoint}",
                    params=params,
                    json=data,
                )
            elif method == "DELETE":
                response = await client.delete(
                    f"{self.GRAPH_URL}/{endpoint}",
                    params=params,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    # === Account Management ===
    
    async def get_me(self) -> Dict[str, Any]:
        """Get current user info."""
        return await self._make_request("GET", "me")
    
    async def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get accessible ad accounts."""
        result = await self._make_request(
            "GET",
            "me/adaccounts",
            params={"fields": "id,name,account_status,currency,timezone_name,business"},
        )
        return result.get("data", [])
    
    async def get_business_accounts(self) -> List[Dict[str, Any]]:
        """Get accessible business accounts."""
        result = await self._make_request(
            "GET",
            "me/businesses",
            params={"fields": "id,name,verification_status"},
        )
        return result.get("data", [])
    
    # === Campaign Management ===
    
    async def list_campaigns(
        self,
        ad_account_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaigns in an ad account."""
        params = {
            "fields": "id,name,status,objective,created_time,start_time,stop_time,daily_budget,lifetime_budget",
        }
        
        if status:
            params["filtering"] = f'[{{"field":"status","operator":"EQUAL","value":"{status}"}}]'
        
        result = await self._make_request(
            "GET",
            f"act_{ad_account_id}/campaigns",
            params=params,
        )
        
        return result.get("data", [])
    
    async def create_campaign(
        self,
        ad_account_id: str,
        name: str,
        objective: str,
        status: str = "PAUSED",
        special_ad_categories: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign."""
        data = {
            "name": name,
            "objective": objective,
            "status": status,
            "special_ad_categories": special_ad_categories or [],
        }
        
        return await self._make_request(
            "POST",
            f"act_{ad_account_id}/campaigns",
            data=data,
        )
    
    async def update_campaign(
        self,
        campaign_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a campaign."""
        return await self._make_request(
            "POST",
            campaign_id,
            data=updates,
        )
    
    async def delete_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Delete (archive) a campaign."""
        return await self.update_campaign(campaign_id, {"status": "DELETED"})
    
    # === Ad Sets ===
    
    async def list_ad_sets(
        self,
        campaign_id: str,
    ) -> List[Dict[str, Any]]:
        """List ad sets in a campaign."""
        result = await self._make_request(
            "GET",
            f"{campaign_id}/adsets",
            params={
                "fields": "id,name,status,targeting,daily_budget,lifetime_budget,bid_strategy,optimization_goal",
            },
        )
        return result.get("data", [])
    
    async def create_ad_set(
        self,
        ad_account_id: str,
        campaign_id: str,
        name: str,
        targeting: Dict[str, Any],
        daily_budget: int,  # in cents
        billing_event: str = "IMPRESSIONS",
        optimization_goal: str = "REACH",
    ) -> Dict[str, Any]:
        """Create a new ad set."""
        data = {
            "name": name,
            "campaign_id": campaign_id,
            "targeting": targeting,
            "daily_budget": daily_budget,
            "billing_event": billing_event,
            "optimization_goal": optimization_goal,
            "status": "PAUSED",
        }
        
        return await self._make_request(
            "POST",
            f"act_{ad_account_id}/adsets",
            data=data,
        )
    
    # === Ads ===
    
    async def list_ads(
        self,
        ad_set_id: str,
    ) -> List[Dict[str, Any]]:
        """List ads in an ad set."""
        result = await self._make_request(
            "GET",
            f"{ad_set_id}/ads",
            params={
                "fields": "id,name,status,creative,tracking_specs",
            },
        )
        return result.get("data", [])
    
    async def create_ad(
        self,
        ad_account_id: str,
        ad_set_id: str,
        name: str,
        creative_id: str,
    ) -> Dict[str, Any]:
        """Create a new ad."""
        data = {
            "name": name,
            "adset_id": ad_set_id,
            "creative": {"creative_id": creative_id},
            "status": "PAUSED",
        }
        
        return await self._make_request(
            "POST",
            f"act_{ad_account_id}/ads",
            data=data,
        )
    
    # === Creatives ===
    
    async def create_ad_creative(
        self,
        ad_account_id: str,
        name: str,
        object_story_spec: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create an ad creative."""
        data = {
            "name": name,
            "object_story_spec": object_story_spec,
        }
        
        return await self._make_request(
            "POST",
            f"act_{ad_account_id}/adcreatives",
            data=data,
        )
    
    # === Insights ===
    
    async def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_30d",
    ) -> Dict[str, Any]:
        """Get campaign performance insights."""
        result = await self._make_request(
            "GET",
            f"{campaign_id}/insights",
            params={
                "date_preset": date_preset,
                "fields": "impressions,reach,clicks,spend,cpc,cpm,ctr,conversions,cost_per_conversion",
            },
        )
        return result.get("data", [{}])[0] if result.get("data") else {}
    
    async def get_account_insights(
        self,
        ad_account_id: str,
        date_preset: str = "last_30d",
    ) -> Dict[str, Any]:
        """Get account-level insights."""
        result = await self._make_request(
            "GET",
            f"act_{ad_account_id}/insights",
            params={
                "date_preset": date_preset,
                "fields": "impressions,reach,clicks,spend,cpc,cpm,ctr,conversions,cost_per_conversion",
            },
        )
        return result.get("data", [{}])[0] if result.get("data") else {}
    
    # === Audiences ===
    
    async def list_custom_audiences(
        self,
        ad_account_id: str,
    ) -> List[Dict[str, Any]]:
        """List custom audiences."""
        result = await self._make_request(
            "GET",
            f"act_{ad_account_id}/customaudiences",
            params={
                "fields": "id,name,subtype,approximate_count",
            },
        )
        return result.get("data", [])
    
    async def create_lookalike_audience(
        self,
        ad_account_id: str,
        name: str,
        origin_audience_id: str,
        country: str = "US",
        ratio: float = 0.01,  # 1%
    ) -> Dict[str, Any]:
        """Create a lookalike audience."""
        data = {
            "name": name,
            "subtype": "LOOKALIKE",
            "origin_audience_id": origin_audience_id,
            "lookalike_spec": {
                "country": country,
                "ratio": ratio,
                "type": "similarity",
            },
        }
        
        return await self._make_request(
            "POST",
            f"act_{ad_account_id}/customaudiences",
            data=data,
        )


# Factory function
def get_meta_ads_service(credentials: Optional[MetaAdsCredential] = None) -> MetaAdsService:
    """Get Meta Ads service instance."""
    return MetaAdsService(credentials)

