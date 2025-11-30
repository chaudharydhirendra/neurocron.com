"""
NeuroCron NeuroPlan & BrainSpark APIs
AI-powered strategy and creative idea generation

AI Tiers Used:
- NeuroPlan (Strategy): Tier 1 - Claude Opus 4.5 (best reasoning)
- BrainSpark (Ideas): Tier 2 - GPT-4.1 (best creative)
"""

from typing import List, Optional
from uuid import UUID, uuid4
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.services.ai import ai_generator, PromptTemplates

logger = logging.getLogger(__name__)
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
    budget_constraint: Optional[str] = "moderate"


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
    Generate a comprehensive 12-month marketing strategy using AI.
    
    Uses Tier 1 (Claude Opus 4.5) for best strategic reasoning.
    
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
    
    # Get prompts for strategy generation
    system_prompt, user_prompt = PromptTemplates.get_strategy_prompt(
        business_name=request.business_name,
        business_description=request.business_description,
        target_audience=request.target_audience,
        goals=request.goals,
        budget_range=request.budget_range,
        timeline_months=request.timeline_months,
        focus_areas=request.focus_areas,
    )
    
    # Generate strategy using AI (Tier 1: Strategic - Claude Opus 4.5)
    logger.info(f"Generating strategy for {request.business_name} using AI")
    ai_response = await ai_generator.generate(
        task_type="strategy",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=4000,
    )
    
    if not ai_response.success:
        logger.error(f"AI generation failed: {ai_response.error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation failed: {ai_response.error}"
        )
    
    # Parse the AI response
    strategy_data = ai_response.as_json
    if not strategy_data:
        logger.error("Failed to parse AI response as JSON")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse strategy response"
        )
    
    # Log cost for monitoring
    logger.info(
        f"Strategy generated: model={ai_response.model_used}, "
        f"tokens_in={ai_response.tokens_in}, tokens_out={ai_response.tokens_out}, "
        f"cost=${ai_response.cost_estimate:.4f}"
    )
    
    # Build response with proper structure
    try:
        quarterly_plans = [
            QuarterlyPlan(**q) for q in strategy_data.get("quarterly_plans", [])
        ]
        channel_strategies = [
            ChannelStrategy(**c) for c in strategy_data.get("channel_strategies", [])
        ]
        
        strategy = MarketingStrategy(
            id=f"strategy-{uuid4()}",
            executive_summary=strategy_data.get("executive_summary", ""),
            vision=strategy_data.get("vision", ""),
            mission=strategy_data.get("mission", ""),
            quarterly_plans=quarterly_plans,
            channel_strategies=channel_strategies,
            competitor_positioning=strategy_data.get("competitor_positioning", ""),
            unique_selling_propositions=strategy_data.get("unique_selling_propositions", []),
            messaging_framework=strategy_data.get("messaging_framework", {}),
            success_metrics=strategy_data.get("success_metrics", []),
            risks_and_mitigations=strategy_data.get("risks_and_mitigations", []),
            total_budget_estimate=strategy_data.get("total_budget_estimate", ""),
        )
        return strategy
    except Exception as e:
        logger.error(f"Failed to structure strategy response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to structure strategy response"
        )


@router.post("/brainspark/generate")
async def generate_ideas(
    request: IdeaGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate creative marketing ideas using AI.
    
    Uses Tier 2 (GPT-4.1) for best creative output.
    
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
    
    # Get prompts for ideas generation
    system_prompt, user_prompt = PromptTemplates.get_ideas_prompt(
        campaign_goal=request.campaign_goal,
        target_audience=request.target_audience,
        brand_tone=request.brand_tone,
        channels=request.channels,
        count=request.count,
        budget_constraint=request.budget_constraint or "moderate",
    )
    
    # Generate ideas using AI (Tier 2: Creative - GPT-4.1)
    logger.info(f"Generating {request.count} creative ideas using AI")
    ai_response = await ai_generator.generate(
        task_type="creative_ideas",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.85,  # Higher temperature for more creative output
        max_tokens=3000,
    )
    
    if not ai_response.success:
        logger.error(f"AI generation failed: {ai_response.error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ideas generation failed: {ai_response.error}"
        )
    
    # Parse the AI response
    ideas_data = ai_response.as_json
    if not ideas_data:
        logger.error("Failed to parse AI response as JSON")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse ideas response"
        )
    
    # Log cost for monitoring
    logger.info(
        f"Ideas generated: model={ai_response.model_used}, "
        f"tokens_in={ai_response.tokens_in}, tokens_out={ai_response.tokens_out}, "
        f"cost=${ai_response.cost_estimate:.4f}"
    )
    
    # Build response
    ideas = []
    for i, idea in enumerate(ideas_data.get("ideas", [])):
        ideas.append(CreativeIdea(
            id=f"idea-{uuid4()}",
            title=idea.get("title", f"Idea {i+1}"),
            category=idea.get("category", "campaign"),
            description=idea.get("description", ""),
            hook=idea.get("hook", ""),
            target_emotion=idea.get("target_emotion", ""),
            estimated_impact=idea.get("estimated_impact", "medium"),
            difficulty=idea.get("difficulty", "medium"),
            timeline=idea.get("timeline", ""),
            required_resources=idea.get("required_resources", []),
            example_execution=idea.get("example_execution", ""),
        ))
    
    return {
        "ideas": [idea.model_dump() for idea in ideas],
        "total": len(ideas),
        "recommendation": ideas_data.get("top_recommendation", "Start with the high-impact, easy-difficulty ideas for quick wins."),
        "combination_suggestion": ideas_data.get("combination_suggestion"),
        "ai_metadata": {
            "model": ai_response.model_used,
            "tier": ai_response.tier.value,
            "cost": ai_response.cost_estimate,
        }
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
                "typical_timeline": 12,
                "budget_range": "medium",
            },
            {
                "id": "ecommerce_launch",
                "name": "E-commerce Launch Strategy",
                "description": "Launch and scale an online store",
                "focus_areas": ["social_commerce", "influencer", "email", "paid_ads"],
                "typical_timeline": 6,
                "budget_range": "medium",
            },
            {
                "id": "local_business",
                "name": "Local Business Domination",
                "description": "Become the go-to in your local market",
                "focus_areas": ["local_seo", "reviews", "community", "google_business"],
                "typical_timeline": 6,
                "budget_range": "low",
            },
            {
                "id": "brand_awareness",
                "name": "Brand Awareness Blitz",
                "description": "Build recognition and trust fast",
                "focus_areas": ["pr", "influencer", "content", "video"],
                "typical_timeline": 3,
                "budget_range": "high",
            },
            {
                "id": "lead_generation",
                "name": "B2B Lead Engine",
                "description": "Systematic lead generation machine",
                "focus_areas": ["linkedin", "content", "webinars", "email"],
                "typical_timeline": 12,
                "budget_range": "medium",
            },
            {
                "id": "product_launch",
                "name": "Product Launch Campaign",
                "description": "Launch a new product with maximum impact",
                "focus_areas": ["pr", "social", "influencer", "email", "paid_ads"],
                "typical_timeline": 3,
                "budget_range": "high",
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
            {"id": "campaign", "name": "Campaign Concepts", "icon": "megaphone", "description": "Full campaign ideas with multiple touchpoints"},
            {"id": "content", "name": "Content Ideas", "icon": "file-text", "description": "Blog posts, videos, podcasts, guides"},
            {"id": "social", "name": "Social Media", "icon": "share", "description": "Engaging social content and series"},
            {"id": "ad", "name": "Ad Angles", "icon": "target", "description": "Creative ad concepts and hooks"},
            {"id": "pr", "name": "PR & Stunts", "icon": "newspaper", "description": "Press-worthy moments and stunts"},
            {"id": "event", "name": "Events & Activations", "icon": "calendar", "description": "Virtual and in-person experiences"},
            {"id": "partnership", "name": "Partnerships", "icon": "handshake", "description": "Co-marketing and collaboration ideas"},
            {"id": "viral", "name": "Viral Hooks", "icon": "trending-up", "description": "Shareable, buzzworthy concepts"},
        ]
    }


@router.get("/ai/status")
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """Get current AI service status and tier information."""
    return {
        "tiers": {
            "strategic": {
                "model": "Claude Opus 4.5",
                "provider": "Anthropic",
                "available": ai_generator.anthropic_available,
                "use_cases": ["Strategy generation", "Competitor analysis", "Business decisions"],
                "cost": "$5/$25 per 1M tokens (in/out)",
            },
            "creative": {
                "model": "GPT-4.1",
                "provider": "OpenAI",
                "available": ai_generator.openai_available,
                "use_cases": ["Creative ideas", "Ad copy", "Personas", "Content writing"],
                "cost": "$10/$30 per 1M tokens (in/out)",
            },
            "standard": {
                "model": "Llama 3.1:8b",
                "provider": "Ollama (local)",
                "available": ai_generator.ollama_available,
                "use_cases": ["Social posts", "Emails", "Chat", "Translations"],
                "cost": "FREE (runs locally)",
            },
        },
        "fallback_chain": "Strategic → Creative → Standard (local)",
        "note": "If a higher tier is unavailable, tasks automatically fall back to the next available tier.",
    }
