"""
Google Ads API Integration
Manage Google Ads campaigns, ad groups, and ads from NeuroCron
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from pydantic import BaseModel


class GoogleAdsConfig:
    """Google Ads API configuration"""
    CLIENT_ID = os.getenv("GOOGLE_ADS_CLIENT_ID")
    CLIENT_SECRET = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
    DEVELOPER_TOKEN = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
    REDIRECT_URI = os.getenv("GOOGLE_ADS_REDIRECT_URI", "https://neurocron.com/integrations/google/callback")
    SCOPES = ["https://www.googleapis.com/auth/adwords"]


class GoogleAdsCredential(BaseModel):
    """OAuth credentials for Google Ads"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    customer_id: Optional[str] = None


class GoogleAdsService:
    """
    Service for interacting with Google Ads API
    
    Features:
    - OAuth authentication flow
    - Campaign management (CRUD)
    - Ad group management
    - Ad creative management
    - Performance metrics
    - Budget management
    - Audience targeting
    """
    
    BASE_URL = "https://googleads.googleapis.com/v14"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    
    def __init__(self, credentials: Optional[GoogleAdsCredential] = None):
        self.credentials = credentials
        self.config = GoogleAdsConfig()
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        params = {
            "client_id": self.config.CLIENT_ID,
            "redirect_uri": self.config.REDIRECT_URI,
            "scope": " ".join(self.config.SCOPES),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"
    
    async def exchange_code(self, code: str) -> GoogleAdsCredential:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.config.CLIENT_ID,
                    "client_secret": self.config.CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.config.REDIRECT_URI,
                },
            )
            response.raise_for_status()
            data = response.json()
            
            return GoogleAdsCredential(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=datetime.utcnow() + timedelta(seconds=data["expires_in"]),
            )
    
    async def refresh_token(self) -> None:
        """Refresh access token using refresh token."""
        if not self.credentials or not self.credentials.refresh_token:
            raise ValueError("No refresh token available")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "client_id": self.config.CLIENT_ID,
                    "client_secret": self.config.CLIENT_SECRET,
                    "refresh_token": self.credentials.refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            response.raise_for_status()
            data = response.json()
            
            self.credentials.access_token = data["access_token"]
            self.credentials.expires_at = datetime.utcnow() + timedelta(seconds=data["expires_in"])
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to Google Ads API."""
        if not self.credentials:
            raise ValueError("No credentials configured")
        
        # Refresh token if expired
        if self.credentials.expires_at <= datetime.utcnow():
            await self.refresh_token()
        
        headers = {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "developer-token": self.config.DEVELOPER_TOKEN,
            "Content-Type": "application/json",
        }
        
        if self.credentials.customer_id:
            headers["login-customer-id"] = self.credentials.customer_id
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=headers,
                )
            elif method == "POST":
                response = await client.post(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=headers,
                    json=data,
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
    
    # === Account Management ===
    
    async def get_accessible_customers(self) -> List[Dict[str, Any]]:
        """Get list of accessible customer accounts."""
        result = await self._make_request(
            "GET",
            "customers:listAccessibleCustomers",
        )
        return result.get("resourceNames", [])
    
    async def get_account_info(self, customer_id: str) -> Dict[str, Any]:
        """Get account information."""
        return await self._make_request(
            "GET",
            f"customers/{customer_id}",
        )
    
    # === Campaign Management ===
    
    async def list_campaigns(
        self,
        customer_id: str,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List campaigns in an account."""
        query = f"""
            SELECT 
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.start_date,
                campaign.end_date,
                campaign_budget.amount_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions
            FROM campaign
            WHERE campaign.status != 'REMOVED'
        """
        
        if status:
            query += f" AND campaign.status = '{status}'"
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}/googleAds:search",
            {"query": query},
        )
        
        return result.get("results", [])
    
    async def create_campaign(
        self,
        customer_id: str,
        name: str,
        campaign_type: str,
        budget_amount: int,  # in micros (1 USD = 1,000,000 micros)
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new campaign."""
        # First create budget
        budget_operation = {
            "create": {
                "name": f"{name} Budget",
                "amount_micros": str(budget_amount),
                "delivery_method": "STANDARD",
            }
        }
        
        budget_result = await self._make_request(
            "POST",
            f"customers/{customer_id}/campaignBudgets:mutate",
            {"operations": [budget_operation]},
        )
        
        budget_resource = budget_result["results"][0]["resourceName"]
        
        # Then create campaign
        campaign_operation = {
            "create": {
                "name": name,
                "status": "PAUSED",
                "advertising_channel_type": campaign_type,
                "campaign_budget": budget_resource,
                "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
            }
        }
        
        if end_date:
            campaign_operation["create"]["end_date"] = end_date
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}/campaigns:mutate",
            {"operations": [campaign_operation]},
        )
        
        return result["results"][0]
    
    async def update_campaign(
        self,
        customer_id: str,
        campaign_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a campaign."""
        operation = {
            "update": {
                "resource_name": f"customers/{customer_id}/campaigns/{campaign_id}",
                **updates,
            },
            "update_mask": ",".join(updates.keys()),
        }
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}/campaigns:mutate",
            {"operations": [operation]},
        )
        
        return result["results"][0]
    
    async def set_campaign_status(
        self,
        customer_id: str,
        campaign_id: str,
        status: str,  # ENABLED, PAUSED, REMOVED
    ) -> Dict[str, Any]:
        """Enable, pause, or remove a campaign."""
        return await self.update_campaign(
            customer_id,
            campaign_id,
            {"status": status},
        )
    
    # === Performance Metrics ===
    
    async def get_campaign_performance(
        self,
        customer_id: str,
        campaign_id: str,
        date_range: str = "LAST_30_DAYS",
    ) -> Dict[str, Any]:
        """Get campaign performance metrics."""
        query = f"""
            SELECT 
                campaign.id,
                campaign.name,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_per_conversion
            FROM campaign
            WHERE campaign.id = {campaign_id}
                AND segments.date DURING {date_range}
        """
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}/googleAds:search",
            {"query": query},
        )
        
        return result.get("results", [{}])[0] if result.get("results") else {}
    
    async def get_account_performance(
        self,
        customer_id: str,
        date_range: str = "LAST_30_DAYS",
    ) -> Dict[str, Any]:
        """Get account-level performance metrics."""
        query = f"""
            SELECT 
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value
            FROM customer
            WHERE segments.date DURING {date_range}
        """
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}/googleAds:search",
            {"query": query},
        )
        
        return result.get("results", [{}])[0] if result.get("results") else {}
    
    # === Keywords ===
    
    async def get_keyword_ideas(
        self,
        customer_id: str,
        keywords: List[str],
        language_id: str = "1000",  # English
        location_ids: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get keyword ideas from Google Ads."""
        location_ids = location_ids or ["2840"]  # United States
        
        data = {
            "keywordSeed": {"keywords": keywords},
            "language": f"languageConstants/{language_id}",
            "geoTargetConstants": [
                f"geoTargetConstants/{loc}" for loc in location_ids
            ],
        }
        
        result = await self._make_request(
            "POST",
            f"customers/{customer_id}:generateKeywordIdeas",
            data,
        )
        
        return result.get("results", [])


# Factory function
def get_google_ads_service(credentials: Optional[GoogleAdsCredential] = None) -> GoogleAdsService:
    """Get Google Ads service instance."""
    return GoogleAdsService(credentials)

