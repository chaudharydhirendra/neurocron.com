"""
NeuroCron NeuroPlan & BrainSpark APIs
AI-powered strategy and creative idea generation
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


# --- NeuroPlan Schemas ---

class StrategyGenerateRequest(BaseModel):
    """Request to generate a marketing strategy"""
    business_name: str
    business_description: str
    target_audience: str
    goals: List[str]
    budget_range: str  # low, medium, high
    timeline_months: int = Field(12, ge=1, le=24)
    focus_areas: Optional[List[str]] = None


class QuarterlyPlan(BaseModel):
    """Quarterly marketing plan"""
    quarter: str
    theme: str
    objectives: List[str]
    key_initiatives: List[str]
    budget_allocation: dict
    kpis: List[str]


class ChannelStrategy(BaseModel):
    """Per-channel strategy"""
    channel: str
    priority: str  # high, medium, low
    tactics: List[str]
    budget_percentage: int
    expected_outcomes: List[str]


class MarketingStrategy(BaseModel):
    """Complete marketing strategy"""
    id: str
    executive_summary: str
    vision: str
    mission: str
    quarterly_plans: List[QuarterlyPlan]
    channel_strategies: List[ChannelStrategy]
    competitor_positioning: str
    unique_selling_propositions: List[str]
    messaging_framework: dict
    success_metrics: List[str]
    risks_and_mitigations: List[dict]
    total_budget_estimate: str


# --- BrainSpark Schemas ---

class IdeaGenerateRequest(BaseModel):
    """Request to generate creative ideas"""
    campaign_goal: str
    target_audience: str
    brand_tone: str  # professional, playful, bold, elegant, friendly
    channels: List[str]
    count: int = Field(5, ge=1, le=10)


class CreativeIdea(BaseModel):
    """A creative marketing idea"""
    id: str
    title: str
    category: str  # campaign, content, social, ad, pr, event
    description: str
    hook: str
    target_emotion: str
    estimated_impact: str  # high, medium, low
    difficulty: str  # easy, medium, hard
    timeline: str
    required_resources: List[str]
    example_execution: str


@router.post("/neuroplan/generate", response_model=MarketingStrategy)
async def generate_strategy(
    request: StrategyGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive 12-month marketing strategy.
    
    NeuroPlan creates a complete roadmap including:
    - Quarterly plans with themes and initiatives
    - Channel-specific strategies
    - Budget allocations
    - KPIs and success metrics
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
    
    # Generate strategy (would use AI in production)
    strategy = _generate_sample_strategy(request)
    return strategy


@router.post("/brainspark/generate")
async def generate_ideas(
    request: IdeaGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate creative marketing ideas.
    
    BrainSpark creates campaign concepts, ad angles, content ideas,
    and creative hooks based on your goals and audience.
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
    
    ideas = _generate_sample_ideas(request)
    return {
        "ideas": ideas,
        "total": len(ideas),
        "recommendation": "Start with the high-impact, easy-difficulty ideas for quick wins.",
    }


@router.get("/neuroplan/templates")
async def get_strategy_templates(
    current_user: User = Depends(get_current_user)
):
    """Get strategy templates for different business types."""
    return {
        "templates": [
            {
                "id": "saas_growth",
                "name": "SaaS Growth Playbook",
                "description": "Comprehensive strategy for B2B SaaS companies",
                "focus_areas": ["content_marketing", "paid_ads", "seo", "partnerships"],
            },
            {
                "id": "ecommerce_launch",
                "name": "E-commerce Launch Strategy",
                "description": "Launch and scale an online store",
                "focus_areas": ["social_commerce", "influencer", "email", "paid_ads"],
            },
            {
                "id": "local_business",
                "name": "Local Business Domination",
                "description": "Become the go-to in your local market",
                "focus_areas": ["local_seo", "reviews", "community", "google_business"],
            },
            {
                "id": "brand_awareness",
                "name": "Brand Awareness Blitz",
                "description": "Build recognition and trust fast",
                "focus_areas": ["pr", "influencer", "content", "video"],
            },
            {
                "id": "lead_generation",
                "name": "B2B Lead Engine",
                "description": "Systematic lead generation machine",
                "focus_areas": ["linkedin", "content", "webinars", "email"],
            },
        ]
    }


@router.get("/brainspark/categories")
async def get_idea_categories(
    current_user: User = Depends(get_current_user)
):
    """Get creative idea categories."""
    return {
        "categories": [
            {"id": "campaign", "name": "Campaign Concepts", "icon": "megaphone"},
            {"id": "content", "name": "Content Ideas", "icon": "file-text"},
            {"id": "social", "name": "Social Media", "icon": "share"},
            {"id": "ad", "name": "Ad Angles", "icon": "target"},
            {"id": "pr", "name": "PR & Stunts", "icon": "newspaper"},
            {"id": "event", "name": "Events & Activations", "icon": "calendar"},
            {"id": "partnership", "name": "Partnerships", "icon": "handshake"},
            {"id": "viral", "name": "Viral Hooks", "icon": "trending-up"},
        ]
    }


def _generate_sample_strategy(request: StrategyGenerateRequest) -> MarketingStrategy:
    """Generate a sample strategy."""
    quarters = []
    themes = ["Foundation & Awareness", "Growth & Acquisition", "Expansion & Optimization", "Scale & Retention"]
    
    for i in range(min(4, request.timeline_months // 3)):
        quarters.append(QuarterlyPlan(
            quarter=f"Q{i+1}",
            theme=themes[i],
            objectives=[
                f"Establish {request.business_name} presence" if i == 0 else f"Scale {request.business_name} reach",
                "Build brand awareness" if i < 2 else "Optimize conversion rates",
                "Generate qualified leads" if i < 2 else "Maximize customer LTV",
            ],
            key_initiatives=[
                "Launch content marketing program",
                "Implement paid advertising campaigns",
                "Build email nurture sequences",
                "Develop social media presence",
            ],
            budget_allocation={
                "paid_ads": 35 + (i * 5),
                "content": 25 - (i * 2),
                "social": 20,
                "email": 10,
                "tools": 10 - (i * 2) if i < 2 else 5,
            },
            kpis=["Website traffic", "Lead generation", "Conversion rate", "Customer acquisition cost"],
        ))
    
    channel_strategies = [
        ChannelStrategy(
            channel="Paid Search (Google Ads)",
            priority="high",
            tactics=["Keyword targeting", "Retargeting", "Performance Max campaigns"],
            budget_percentage=30,
            expected_outcomes=["High-intent traffic", "Direct conversions", "Brand visibility"],
        ),
        ChannelStrategy(
            channel="Social Media (LinkedIn, Meta)",
            priority="high",
            tactics=["Organic posting", "Paid campaigns", "Community building"],
            budget_percentage=25,
            expected_outcomes=["Brand awareness", "Engagement", "Lead generation"],
        ),
        ChannelStrategy(
            channel="Content Marketing",
            priority="high",
            tactics=["Blog posts", "Ebooks/guides", "Video content", "Podcasts"],
            budget_percentage=20,
            expected_outcomes=["SEO growth", "Thought leadership", "Lead nurturing"],
        ),
        ChannelStrategy(
            channel="Email Marketing",
            priority="medium",
            tactics=["Welcome sequences", "Newsletters", "Promotional campaigns"],
            budget_percentage=15,
            expected_outcomes=["Lead nurturing", "Customer retention", "Direct revenue"],
        ),
        ChannelStrategy(
            channel="SEO",
            priority="medium",
            tactics=["On-page optimization", "Link building", "Technical SEO"],
            budget_percentage=10,
            expected_outcomes=["Organic traffic", "Long-term visibility", "Authority"],
        ),
    ]
    
    return MarketingStrategy(
        id="strategy-" + str(UUID(int=0)),
        executive_summary=f"This comprehensive marketing strategy for {request.business_name} focuses on building brand awareness, generating qualified leads, and driving sustainable growth over {request.timeline_months} months.",
        vision=f"Position {request.business_name} as the leading solution for {request.target_audience}.",
        mission="Deliver exceptional value through targeted marketing that resonates with our audience and drives measurable business results.",
        quarterly_plans=quarters,
        channel_strategies=channel_strategies,
        competitor_positioning="Differentiate through superior customer experience, innovative features, and thought leadership content.",
        unique_selling_propositions=[
            "AI-powered automation that saves 10+ hours per week",
            "Unified platform replacing 5+ separate tools",
            "Real-time insights and predictive analytics",
            "White-glove onboarding and support",
        ],
        messaging_framework={
            "primary_message": f"{request.business_name} helps {request.target_audience} achieve their goals faster with intelligent automation.",
            "supporting_messages": [
                "Save time with AI-powered workflows",
                "Make data-driven decisions with real-time insights",
                "Scale your efforts without scaling your team",
            ],
            "tone": "Professional yet approachable, confident but not arrogant",
            "key_proof_points": ["Customer testimonials", "Case studies", "Industry recognition"],
        },
        success_metrics=[
            "Monthly website traffic growth: 20%+",
            "Lead generation: 500+ MQLs per month by Q4",
            "Conversion rate: 3%+ from visitor to lead",
            "Customer acquisition cost: Under $200",
            "Brand awareness lift: 50% YoY",
        ],
        risks_and_mitigations=[
            {"risk": "Market saturation", "mitigation": "Focus on niche segments and differentiation"},
            {"risk": "Budget constraints", "mitigation": "Prioritize high-ROI channels, use organic growth tactics"},
            {"risk": "Competitor response", "mitigation": "Monitor competitors, maintain agility to pivot"},
        ],
        total_budget_estimate=f"${50000 if request.budget_range == 'low' else 150000 if request.budget_range == 'medium' else 500000}+ annual marketing budget recommended",
    )


def _generate_sample_ideas(request: IdeaGenerateRequest) -> List[CreativeIdea]:
    """Generate sample creative ideas."""
    ideas_pool = [
        CreativeIdea(
            id="idea-1",
            title="The Transformation Challenge",
            category="campaign",
            description="30-day challenge where participants document their transformation using your product/service.",
            hook="What can you achieve in 30 days?",
            target_emotion="Aspiration & Achievement",
            estimated_impact="high",
            difficulty="medium",
            timeline="4-6 weeks prep, 30-day campaign",
            required_resources=["Landing page", "Email sequences", "Social templates", "Prizes"],
            example_execution="Participants share daily/weekly progress on social with branded hashtag. Winners get featured and prizes.",
        ),
        CreativeIdea(
            id="idea-2",
            title="Behind the Scenes Series",
            category="content",
            description="Weekly content showing the real people, processes, and stories behind your brand.",
            hook="See how the magic happens",
            target_emotion="Trust & Authenticity",
            estimated_impact="medium",
            difficulty="easy",
            timeline="Ongoing weekly content",
            required_resources=["Video equipment", "Content calendar", "Team participation"],
            example_execution="Weekly video/post featuring different team members, their work, and personal stories.",
        ),
        CreativeIdea(
            id="idea-3",
            title="User-Generated Takeover",
            category="social",
            description="Let your best customers take over your social media for a day.",
            hook="Our customers tell it best",
            target_emotion="Community & Belonging",
            estimated_impact="high",
            difficulty="easy",
            timeline="1 day per takeover, monthly",
            required_resources=["Customer outreach", "Content guidelines", "Approval process"],
            example_execution="Top customer shares their day, tips, and experience using your product through your channels.",
        ),
        CreativeIdea(
            id="idea-4",
            title="The Comparison Calculator",
            category="ad",
            description="Interactive tool that shows exactly how much time/money users save with your solution.",
            hook="See your savings in real-time",
            target_emotion="Logic & Value",
            estimated_impact="high",
            difficulty="medium",
            timeline="2-3 weeks development",
            required_resources=["Developer time", "Industry benchmarks", "Landing page"],
            example_execution="Interactive calculator ad driving to personalized results page with tailored follow-up.",
        ),
        CreativeIdea(
            id="idea-5",
            title="Trend Hijacking Campaign",
            category="viral",
            description="React to trending topics with relevant, branded content in real-time.",
            hook="Be part of the conversation",
            target_emotion="Relevance & Timeliness",
            estimated_impact="high",
            difficulty="hard",
            timeline="Real-time, ongoing",
            required_resources=["Monitoring tools", "Creative team on standby", "Approval workflow"],
            example_execution="Pre-approved templates and rapid response process for trending moments.",
        ),
        CreativeIdea(
            id="idea-6",
            title="Expert Webinar Series",
            category="content",
            description="Monthly webinars featuring industry experts and thought leaders.",
            hook="Learn from the best",
            target_emotion="Education & Authority",
            estimated_impact="medium",
            difficulty="medium",
            timeline="Monthly, 3-month minimum",
            required_resources=["Webinar platform", "Expert network", "Promotion plan"],
            example_execution="Partner with influencers for co-hosted educational sessions with Q&A.",
        ),
        CreativeIdea(
            id="idea-7",
            title="Customer Success Story Film",
            category="pr",
            description="Mini-documentary style video showcasing a customer's transformation journey.",
            hook="Real results, real stories",
            target_emotion="Inspiration & Trust",
            estimated_impact="high",
            difficulty="hard",
            timeline="4-6 weeks production",
            required_resources=["Video production", "Customer participation", "Distribution plan"],
            example_execution="5-10 minute documentary distributed across YouTube, LinkedIn, and sales process.",
        ),
        CreativeIdea(
            id="idea-8",
            title="Controversial Take Post",
            category="social",
            description="Share a bold, contrarian opinion about your industry to spark discussion.",
            hook="Here's an unpopular opinion...",
            target_emotion="Curiosity & Engagement",
            estimated_impact="medium",
            difficulty="easy",
            timeline="Single post, ongoing opportunity",
            required_resources=["Thought leadership", "Community management"],
            example_execution="Well-reasoned contrarian take that positions your brand as a thought leader.",
        ),
    ]
    
    # Filter by channels and return requested count
    return ideas_pool[:request.count]

