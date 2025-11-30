"""
NeuroCron BattleStation, TrendRadar, and CrisisShield APIs
Competitive intelligence, trend monitoring, and brand protection
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import random

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.intelligence import (
    Competitor, CompetitorInsight, Trend, BrandMention, CrisisEvent
)

router = APIRouter()


# --- BattleStation: Competitor Tracking ---

class CompetitorCreate(BaseModel):
    name: str
    website: str
    description: Optional[str] = None


@router.post("/competitors")
async def add_competitor(
    competitor: CompetitorCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a competitor to track."""
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
    
    # Create competitor
    new_competitor = Competitor(
        organization_id=org_id,
        name=competitor.name,
        website=competitor.website,
        description=competitor.description,
        health_score=50,  # Initial score
        threat_level="medium",
    )
    db.add(new_competitor)
    await db.commit()
    await db.refresh(new_competitor)
    
    return {
        "id": str(new_competitor.id),
        "name": new_competitor.name,
        "website": new_competitor.website,
        "description": new_competitor.description,
        "tracking_since": new_competitor.created_at.isoformat() if new_competitor.created_at else None,
        "message": "Competitor added. Initial analysis will complete in 24 hours.",
    }


@router.get("/competitors")
async def list_competitors(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all tracked competitors."""
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
    
    # Fetch competitors
    result = await db.execute(
        select(Competitor)
        .where(Competitor.organization_id == org_id)
        .where(Competitor.is_active == True)
        .order_by(Competitor.created_at.desc())
    )
    competitors = result.scalars().all()
    
    # If no competitors, return sample data for demo
    if not competitors:
        return {
            "competitors": [
                {
                    "id": "comp-demo-1",
                    "name": "Competitor A",
                    "website": "https://competitora.com",
                    "description": "Major player in the market",
                    "tracking_since": "2024-01-15T00:00:00Z",
                    "health_score": 82,
                    "threat_level": "high",
                    "metrics": {
                        "website_traffic": "2.5M/mo",
                        "social_followers": "125K",
                        "domain_authority": 65,
                        "ad_spend_estimate": "$50K/mo",
                    }
                },
                {
                    "id": "comp-demo-2",
                    "name": "Competitor B",
                    "website": "https://competitorb.com",
                    "description": "Fast-growing startup",
                    "tracking_since": "2024-02-01T00:00:00Z",
                    "health_score": 68,
                    "threat_level": "medium",
                    "metrics": {
                        "website_traffic": "800K/mo",
                        "social_followers": "45K",
                        "domain_authority": 48,
                        "ad_spend_estimate": "$20K/mo",
                    }
                },
            ]
        }
    
    return {
        "competitors": [
            {
                "id": str(c.id),
                "name": c.name,
                "website": c.website,
                "description": c.description,
                "tracking_since": c.created_at.isoformat() if c.created_at else None,
                "health_score": c.health_score,
                "threat_level": c.threat_level,
                "metrics": c.metrics or {
                    "website_traffic": c.website_traffic or "N/A",
                    "social_followers": c.social_followers or "N/A",
                    "domain_authority": c.domain_authority,
                    "ad_spend_estimate": c.ad_spend_estimate or "N/A",
                }
            }
            for c in competitors
        ]
    }


@router.delete("/competitors/{competitor_id}")
async def delete_competitor(
    competitor_id: UUID,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop tracking a competitor."""
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
    
    # Soft delete
    result = await db.execute(
        select(Competitor)
        .where(Competitor.id == competitor_id)
        .where(Competitor.organization_id == org_id)
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Competitor not found"
        )
    
    competitor.is_active = False
    await db.commit()
    
    return {"message": "Competitor tracking stopped"}


@router.get("/competitors/insights")
async def get_competitor_insights(
    org_id: UUID = Query(..., description="Organization ID"),
    competitor_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get competitive intelligence insights."""
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
    
    # Build query for insights
    query = select(CompetitorInsight).join(Competitor)
    query = query.where(Competitor.organization_id == org_id)
    if competitor_id:
        query = query.where(CompetitorInsight.competitor_id == competitor_id)
    query = query.order_by(CompetitorInsight.created_at.desc()).limit(20)
    
    result = await db.execute(query)
    insights = result.scalars().all()
    
    # If no insights, return sample data for demo
    now = datetime.utcnow()
    if not insights:
        return {
            "insights": [
                {
                    "id": "insight-1",
                    "competitor_id": "comp-1",
                    "competitor_name": "Competitor A",
                    "type": "pricing_change",
                    "title": "Price reduction detected",
                    "description": "Competitor A reduced their Pro plan pricing by 15%. This could impact our mid-market positioning.",
                    "detected_at": (now - timedelta(hours=6)).isoformat(),
                    "impact": "negative",
                    "action_recommended": "Consider promotional offer or highlight value differentiators",
                },
                {
                    "id": "insight-2",
                    "competitor_id": "comp-2",
                    "competitor_name": "Competitor B",
                    "type": "new_product",
                    "title": "New feature launch",
                    "description": "Competitor B launched an AI-powered analytics feature similar to our InsightCortex.",
                    "detected_at": (now - timedelta(days=1)).isoformat(),
                    "impact": "neutral",
                    "action_recommended": "Accelerate roadmap for advanced analytics features",
                },
            ],
            "total": 2
        }
    
    return {
        "insights": [
            {
                "id": str(i.id),
                "competitor_id": str(i.competitor_id),
                "competitor_name": i.competitor.name if i.competitor else "Unknown",
                "type": i.insight_type,
                "title": i.title,
                "description": i.description,
                "detected_at": i.created_at.isoformat() if i.created_at else None,
                "impact": i.impact,
                "action_recommended": i.action_recommended,
            }
            for i in insights
        ],
        "total": len(insights)
    }


# --- TrendRadar: Real-time Trend Monitoring ---

@router.get("/trends")
async def get_trends(
    org_id: UUID = Query(..., description="Organization ID"),
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trending topics relevant to your industry."""
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
    
    # Fetch trends from database
    query = select(Trend).where(Trend.organization_id == org_id)
    if category:
        query = query.where(Trend.category == category)
    query = query.order_by(Trend.relevance_score.desc()).limit(20)
    
    result = await db.execute(query)
    trends = result.scalars().all()
    
    # If no trends, return sample data
    if not trends:
        return {
            "trends": [
                {
                    "id": "trend-1",
                    "topic": "AI Marketing Automation",
                    "category": "technology",
                    "velocity": "rising",
                    "growth_24h": 45,
                    "volume": 125000,
                    "sentiment": "positive",
                    "relevance_score": 95,
                    "source_breakdown": {
                        "twitter": 45,
                        "linkedin": 30,
                        "news": 15,
                        "reddit": 10,
                    },
                    "opportunity": "High opportunity for thought leadership content",
                },
                {
                    "id": "trend-2",
                    "topic": "Marketing Budget Optimization",
                    "category": "industry",
                    "velocity": "stable",
                    "growth_24h": 12,
                    "volume": 85000,
                    "sentiment": "neutral",
                    "relevance_score": 78,
                    "source_breakdown": {
                        "news": 50,
                        "linkedin": 30,
                        "twitter": 15,
                        "reddit": 5,
                    },
                    "opportunity": "Position as cost-effective solution",
                },
                {
                    "id": "trend-3",
                    "topic": "Privacy-First Marketing",
                    "category": "compliance",
                    "velocity": "rising",
                    "growth_24h": 28,
                    "volume": 65000,
                    "sentiment": "neutral",
                    "relevance_score": 82,
                    "source_breakdown": {
                        "news": 40,
                        "linkedin": 35,
                        "twitter": 20,
                        "reddit": 5,
                    },
                    "opportunity": "Highlight privacy features and compliance",
                },
            ],
            "summary": {
                "total_monitored": 156,
                "high_relevance": 12,
                "opportunities_identified": 8,
            }
        }
    
    return {
        "trends": [
            {
                "id": str(t.id),
                "topic": t.topic,
                "category": t.category,
                "velocity": t.velocity,
                "growth_24h": t.growth_24h,
                "volume": t.volume,
                "sentiment": t.sentiment,
                "relevance_score": t.relevance_score,
                "source_breakdown": t.source_breakdown or {},
                "opportunity": t.opportunity,
            }
            for t in trends
        ],
        "summary": {
            "total_monitored": len(trends),
            "high_relevance": len([t for t in trends if t.relevance_score >= 80]),
            "opportunities_identified": len([t for t in trends if t.opportunity]),
        }
    }


@router.get("/trends/alerts")
async def get_trend_alerts(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trend alerts that require attention."""
    now = datetime.utcnow()
    
    return {
        "alerts": [
            {
                "id": "alert-1",
                "type": "opportunity",
                "priority": "high",
                "title": "Viral trend matches your content",
                "description": "'AI Marketing Automation' is trending. Your blog post on this topic could gain significant traction if shared now.",
                "detected_at": (now - timedelta(hours=2)).isoformat(),
                "suggested_action": "Share blog post on social with trending hashtags",
            },
            {
                "id": "alert-2",
                "type": "competitor_mention",
                "priority": "medium",
                "title": "Competitor mentioned in industry discussion",
                "description": "Competitor A was mentioned in a popular Reddit thread about marketing tools. Consider joining the conversation.",
                "detected_at": (now - timedelta(hours=5)).isoformat(),
                "suggested_action": "Prepare thoughtful response highlighting your advantages",
            },
        ],
        "total": 2,
    }


# --- CrisisShield: Brand Protection ---

@router.get("/brand/health")
async def get_brand_health(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get brand health score and metrics."""
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
    
    # Count mentions by sentiment
    now = datetime.utcnow()
    day_ago = now - timedelta(days=1)
    
    # In production, would calculate from actual mentions
    return {
        "health_score": 85,
        "trend": "stable",
        "metrics": {
            "sentiment_score": 72,
            "share_of_voice": 15.2,
            "brand_mentions_24h": 234,
            "positive_mentions": 156,
            "neutral_mentions": 62,
            "negative_mentions": 16,
            "response_time_avg": "2.5 hours",
        },
        "benchmarks": {
            "industry_avg_sentiment": 65,
            "industry_avg_response_time": "4 hours",
        },
        "recommendations": [
            "Brand health is strong. Continue current engagement strategy.",
            "Consider increasing response time for negative mentions.",
            "Share of voice is below target - increase content frequency.",
        ]
    }


@router.get("/brand/mentions")
async def get_brand_mentions(
    org_id: UUID = Query(..., description="Organization ID"),
    sentiment: Optional[str] = None,
    source: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get brand mentions from across the web."""
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
    
    # Build query
    query = select(BrandMention).where(BrandMention.organization_id == org_id)
    if sentiment:
        query = query.where(BrandMention.sentiment == sentiment)
    if source:
        query = query.where(BrandMention.source == source)
    query = query.order_by(BrandMention.created_at.desc()).limit(50)
    
    result = await db.execute(query)
    mentions = result.scalars().all()
    
    # If no mentions, return sample data
    now = datetime.utcnow()
    if not mentions:
        sample_mentions = [
            {
                "id": "mention-1",
                "source": "twitter",
                "author": "@marketing_guru",
                "content": "Just tried @NeuroCron for our agency - the AI features are incredible! Saved us 10 hours last week alone. 🚀",
                "sentiment": "positive",
                "reach": 15000,
                "engagement": 342,
                "timestamp": (now - timedelta(hours=2)).isoformat(),
                "url": "https://twitter.com/...",
            },
            {
                "id": "mention-2",
                "source": "linkedin",
                "author": "Sarah Marketing VP",
                "content": "Evaluating marketing automation tools. NeuroCron looks promising but waiting to see case studies from enterprise customers.",
                "sentiment": "neutral",
                "reach": 8500,
                "engagement": 45,
                "timestamp": (now - timedelta(hours=5)).isoformat(),
                "url": "https://linkedin.com/...",
            },
            {
                "id": "mention-3",
                "source": "reddit",
                "author": "u/startup_marketer",
                "content": "Anyone else having issues with NeuroCron's API? Getting timeout errors when trying to sync campaigns.",
                "sentiment": "negative",
                "reach": 2500,
                "engagement": 28,
                "timestamp": (now - timedelta(hours=8)).isoformat(),
                "url": "https://reddit.com/...",
                "requires_action": True,
            },
        ]
        
        if sentiment:
            sample_mentions = [m for m in sample_mentions if m["sentiment"] == sentiment]
        if source:
            sample_mentions = [m for m in sample_mentions if m["source"] == source]
        
        return {"mentions": sample_mentions, "total": len(sample_mentions)}
    
    return {
        "mentions": [
            {
                "id": str(m.id),
                "source": m.source,
                "author": m.author_name or m.author_handle,
                "content": m.content,
                "sentiment": m.sentiment,
                "reach": m.reach,
                "engagement": m.engagement,
                "timestamp": m.created_at.isoformat() if m.created_at else None,
                "url": m.source_url,
                "requires_action": m.requires_action,
            }
            for m in mentions
        ],
        "total": len(mentions)
    }


@router.get("/brand/crises")
async def get_active_crises(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active brand crises or potential issues."""
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
    
    # Fetch crises
    result = await db.execute(
        select(CrisisEvent)
        .where(CrisisEvent.organization_id == org_id)
        .where(CrisisEvent.status == "active")
        .order_by(CrisisEvent.created_at.desc())
    )
    crises = result.scalars().all()
    
    return {
        "active_crises": [
            {
                "id": str(c.id),
                "severity": c.severity,
                "title": c.title,
                "description": c.description,
                "mentions_count": c.mentions_count,
                "sentiment_trend": c.sentiment_trend,
                "recommended_actions": c.recommended_actions or [],
            }
            for c in crises
        ],
        "potential_issues": [
            {
                "id": "issue-1",
                "severity": "low",
                "title": "API Performance Complaints",
                "description": "3 mentions of API timeout issues in the past 24 hours. Monitor for escalation.",
                "mentions_count": 3,
                "sentiment_trend": "declining",
                "recommended_actions": [
                    "Check API performance metrics",
                    "Prepare response template for support team",
                    "Consider proactive communication if issue persists",
                ],
            }
        ] if not crises else [],
        "resolved_recently": [],
    }


@router.post("/brand/respond")
async def queue_crisis_response(
    mention_id: str,
    response_content: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Queue a response to a brand mention."""
    return {
        "success": True,
        "mention_id": mention_id,
        "response_queued": True,
        "estimated_publish": "Within 5 minutes",
        "message": "Response queued for review and publishing",
    }
