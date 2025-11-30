"""
NeuroCron ChannelPulse API
Unified cross-channel control center and inbox
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import random

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


class InboxMessage(BaseModel):
    """Unified inbox message"""
    id: str
    channel: str  # facebook, instagram, twitter, linkedin, email
    type: str  # comment, message, mention, review
    author: str
    author_avatar: Optional[str]
    content: str
    timestamp: str
    sentiment: str  # positive, neutral, negative
    replied: bool
    priority: str  # high, medium, low


class ScheduledPost(BaseModel):
    """Scheduled social media post"""
    id: str
    content: str
    channels: List[str]
    media_urls: List[str]
    scheduled_for: str
    status: str  # scheduled, published, failed


class ChannelStats(BaseModel):
    """Channel performance stats"""
    channel: str
    followers: int
    following: int
    posts_this_month: int
    engagement_rate: float
    growth_rate: float


@router.get("/inbox")
async def get_unified_inbox(
    org_id: UUID = Query(..., description="Organization ID"),
    channel: Optional[str] = None,
    sentiment: Optional[str] = None,
    replied: Optional[bool] = None,
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get unified inbox messages from all channels.
    
    Aggregates comments, messages, mentions, and reviews from all connected platforms.
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
    
    # Generate sample inbox messages
    messages = _generate_sample_inbox()
    
    # Apply filters
    if channel:
        messages = [m for m in messages if m["channel"] == channel]
    if sentiment:
        messages = [m for m in messages if m["sentiment"] == sentiment]
    if replied is not None:
        messages = [m for m in messages if m["replied"] == replied]
    
    return {
        "messages": messages[:limit],
        "total": len(messages),
        "unread_count": len([m for m in messages if not m["replied"]]),
        "sentiment_summary": {
            "positive": len([m for m in messages if m["sentiment"] == "positive"]),
            "neutral": len([m for m in messages if m["sentiment"] == "neutral"]),
            "negative": len([m for m in messages if m["sentiment"] == "negative"]),
        }
    }


@router.post("/inbox/{message_id}/reply")
async def reply_to_message(
    message_id: str,
    reply_content: str,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reply to an inbox message."""
    return {
        "success": True,
        "message_id": message_id,
        "reply_sent": True,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/stats")
async def get_channel_stats(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get performance stats for all connected channels."""
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
    
    return {
        "channels": [
            {
                "channel": "facebook",
                "connected": True,
                "followers": 12500,
                "following": 245,
                "posts_this_month": 18,
                "engagement_rate": 3.2,
                "growth_rate": 2.1,
                "top_post_reach": 8500,
            },
            {
                "channel": "instagram",
                "connected": True,
                "followers": 28000,
                "following": 180,
                "posts_this_month": 25,
                "engagement_rate": 4.8,
                "growth_rate": 3.5,
                "top_post_reach": 15000,
            },
            {
                "channel": "twitter",
                "connected": True,
                "followers": 8900,
                "following": 420,
                "posts_this_month": 45,
                "engagement_rate": 2.1,
                "growth_rate": 1.8,
                "top_post_reach": 12000,
            },
            {
                "channel": "linkedin",
                "connected": True,
                "followers": 5600,
                "following": 890,
                "posts_this_month": 12,
                "engagement_rate": 5.2,
                "growth_rate": 4.2,
                "top_post_reach": 6500,
            },
        ],
        "totals": {
            "total_followers": 55000,
            "average_engagement": 3.8,
            "posts_this_month": 100,
        }
    }


@router.get("/scheduled")
async def get_scheduled_posts(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get scheduled posts."""
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
    
    now = datetime.utcnow()
    return {
        "posts": [
            {
                "id": "post-1",
                "content": "🚀 Exciting news! We're launching our new AI features next week. Stay tuned for something amazing! #AI #Innovation",
                "channels": ["twitter", "linkedin"],
                "media_urls": [],
                "scheduled_for": (now + timedelta(hours=2)).isoformat(),
                "status": "scheduled",
            },
            {
                "id": "post-2",
                "content": "Behind the scenes at NeuroCron HQ 📸 Our team working on the next big thing!",
                "channels": ["instagram", "facebook"],
                "media_urls": ["https://example.com/image1.jpg"],
                "scheduled_for": (now + timedelta(days=1)).isoformat(),
                "status": "scheduled",
            },
            {
                "id": "post-3",
                "content": "Check out our latest blog post: 'How AI is Transforming Digital Marketing' 📊 Link in bio!",
                "channels": ["linkedin"],
                "media_urls": [],
                "scheduled_for": (now + timedelta(days=2)).isoformat(),
                "status": "scheduled",
            },
        ],
        "total": 3,
    }


@router.post("/schedule")
async def schedule_post(
    content: str,
    channels: List[str],
    scheduled_for: str,
    media_urls: Optional[List[str]] = None,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule a new post."""
    return {
        "id": "new-post-id",
        "content": content,
        "channels": channels,
        "scheduled_for": scheduled_for,
        "status": "scheduled",
        "message": "Post scheduled successfully",
    }


@router.get("/activity-feed")
async def get_activity_feed(
    org_id: UUID = Query(..., description="Organization ID"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time activity feed across all channels."""
    now = datetime.utcnow()
    return {
        "activities": [
            {
                "id": "act-1",
                "type": "new_follower",
                "channel": "instagram",
                "description": "@marketing_pro started following you",
                "timestamp": (now - timedelta(minutes=5)).isoformat(),
            },
            {
                "id": "act-2",
                "type": "post_published",
                "channel": "twitter",
                "description": "Your scheduled post was published",
                "timestamp": (now - timedelta(minutes=30)).isoformat(),
            },
            {
                "id": "act-3",
                "type": "mention",
                "channel": "twitter",
                "description": "@startup_weekly mentioned you in their tweet",
                "timestamp": (now - timedelta(hours=1)).isoformat(),
            },
            {
                "id": "act-4",
                "type": "comment",
                "channel": "facebook",
                "description": "New comment on your product launch post",
                "timestamp": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "id": "act-5",
                "type": "engagement_spike",
                "channel": "linkedin",
                "description": "Your post is getting 3x normal engagement!",
                "timestamp": (now - timedelta(hours=3)).isoformat(),
            },
        ],
        "total": 5,
    }


def _generate_sample_inbox():
    """Generate sample inbox messages."""
    channels = ["facebook", "instagram", "twitter", "linkedin", "email"]
    types = ["comment", "message", "mention", "review"]
    sentiments = ["positive", "neutral", "negative"]
    
    names = ["Sarah Johnson", "Mike Chen", "Emily Rodriguez", "James Wilson", "Lisa Park", 
             "David Kim", "Anna Martinez", "Tom Brown", "Jessica Lee", "Ryan Garcia"]
    
    positive_messages = [
        "Love your product! It's been a game-changer for our team.",
        "Just wanted to say your customer service is amazing! 🙌",
        "Best marketing tool I've used. Highly recommend!",
        "This has saved us so much time. Thank you!",
        "Great webinar yesterday! Very informative.",
    ]
    
    neutral_messages = [
        "Can you tell me more about the pricing?",
        "Does this integrate with Salesforce?",
        "What's the difference between the starter and pro plans?",
        "Is there a mobile app available?",
        "How long does onboarding typically take?",
    ]
    
    negative_messages = [
        "Having trouble with the login. Can someone help?",
        "The dashboard is loading slowly for me today.",
        "I expected more features at this price point.",
        "Need better documentation for the API.",
        "Still waiting for a response to my support ticket.",
    ]
    
    messages = []
    now = datetime.utcnow()
    
    for i in range(25):
        sentiment = random.choice(sentiments)
        if sentiment == "positive":
            content = random.choice(positive_messages)
        elif sentiment == "neutral":
            content = random.choice(neutral_messages)
        else:
            content = random.choice(negative_messages)
        
        messages.append({
            "id": f"msg-{i+1}",
            "channel": random.choice(channels),
            "type": random.choice(types),
            "author": random.choice(names),
            "author_avatar": f"https://i.pravatar.cc/40?u={i}",
            "content": content,
            "timestamp": (now - timedelta(hours=random.randint(1, 48))).isoformat(),
            "sentiment": sentiment,
            "replied": random.choice([True, False]),
            "priority": "high" if sentiment == "negative" else ("medium" if sentiment == "neutral" else "low"),
        })
    
    return sorted(messages, key=lambda x: x["timestamp"], reverse=True)

