"""
NeuroCron Campaign Schemas
Pydantic models for campaign-related requests/responses
"""

from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.campaign import CampaignStatus, CampaignType, ContentType


class CampaignBase(BaseModel):
    """Base campaign schema"""
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    campaign_type: CampaignType


class CampaignCreate(CampaignBase):
    """Schema for creating a campaign"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, ge=0)
    target_audience: Optional[dict] = None
    channels: Optional[List[str]] = None
    goals: Optional[dict] = None


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, ge=0)
    target_audience: Optional[dict] = None
    channels: Optional[List[str]] = None
    goals: Optional[dict] = None


class ContentResponse(BaseModel):
    """Campaign content response"""
    id: UUID
    title: str
    content_type: ContentType
    status: str
    channel: Optional[str] = None
    platform: Optional[str] = None
    ai_generated: bool
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class CampaignResponse(CampaignBase):
    """Schema for campaign response"""
    id: UUID
    organization_id: UUID
    status: CampaignStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    spent: float
    target_audience: Optional[dict] = None
    channels: Optional[List[str]] = None
    goals: Optional[dict] = None
    strategy: Optional[dict] = None
    metrics: Optional[dict] = None
    contents: Optional[List[ContentResponse]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignContentCreate(BaseModel):
    """Schema for creating campaign content"""
    title: str = Field(..., min_length=2, max_length=500)
    content_type: ContentType
    body: Optional[str] = None
    channel: Optional[str] = None
    platform: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class CampaignAnalytics(BaseModel):
    """Campaign analytics summary"""
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    spend: float = 0.0
    ctr: float = 0.0
    cpc: float = 0.0
    cpa: float = 0.0
    roas: float = 0.0

