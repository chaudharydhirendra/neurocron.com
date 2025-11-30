"""
NeuroCron ContentForge API
AI-powered content generation for all marketing channels

AI Tiers Used:
- Blog content: Tier 2 (GPT-4.1) - best for long-form creative writing
- Social posts: Tier 3 (Llama 3.1) - FREE, good for short content
- Emails: Tier 3 (Llama 3.1) - FREE, good for formatted content
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
from app.models.user import User
from app.models.organization import OrganizationMember
from app.services.ai import ai_generator, PromptTemplates, AITier

logger = logging.getLogger(__name__)
router = APIRouter()


class ContentGenerateRequest(BaseModel):
    """Request schema for content generation"""
    content_type: str = Field(..., description="Type: social_post, blog, email, ad_copy, landing_page")
    topic: str = Field(..., description="Main topic or subject")
    platform: Optional[str] = Field(None, description="Target platform (instagram, twitter, linkedin, etc.)")
    tone: Optional[str] = Field("professional", description="Tone: professional, casual, humorous, inspiring")
    length: Optional[str] = Field("medium", description="Length: short, medium, long")
    keywords: Optional[List[str]] = Field(None, description="Keywords to include")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    additional_instructions: Optional[str] = Field(None, description="Any additional instructions")


class ContentVariation(BaseModel):
    """Single content variation"""
    id: str
    content: str
    hashtags: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    estimated_engagement: Optional[str] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None


class ContentGenerateResponse(BaseModel):
    """Response schema for content generation"""
    variations: List[ContentVariation]
    metadata: dict


class IdeaGenerateRequest(BaseModel):
    """Request for content idea generation"""
    topic: Optional[str] = None
    industry: Optional[str] = None
    target_audience: Optional[str] = None
    count: int = Field(5, ge=1, le=20)


class ContentIdea(BaseModel):
    """Single content idea"""
    id: str
    title: str
    description: str
    content_type: str
    suggested_platforms: List[str]
    trending_score: Optional[float] = None


class IdeaGenerateResponse(BaseModel):
    """Response for idea generation"""
    ideas: List[ContentIdea]


@router.post("/generate", response_model=ContentGenerateResponse)
async def generate_content(
    request: ContentGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    variations: int = Query(3, ge=1, le=5, description="Number of variations"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate marketing content using AI.
    
    AI Tier Selection:
    - Blog/landing_page: Tier 2 (GPT-4.1) - best for long-form creative
    - Social/email: Tier 3 (Llama 3.1) - FREE, good for short content
    
    Supports multiple content types:
    - social_post: Social media posts for various platforms
    - blog: Blog articles and long-form content
    - email: Email marketing content
    - ad_copy: Advertising copy for paid campaigns
    - landing_page: Landing page copy and sections
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
    
    # Route to appropriate AI tier and prompt based on content type
    content_type = request.content_type.lower()
    
    if content_type == "blog":
        return await _generate_blog_content(request, variations)
    elif content_type == "social_post":
        return await _generate_social_content(request, variations)
    elif content_type == "email":
        return await _generate_email_content(request, variations)
    elif content_type == "ad_copy":
        # Use ad-specific generation
        return await _generate_ad_content(request, variations)
    else:
        # Default to blog-style generation for landing_page etc
        return await _generate_blog_content(request, variations)


async def _generate_blog_content(
    request: ContentGenerateRequest,
    variations: int
) -> ContentGenerateResponse:
    """Generate blog/long-form content using Tier 2 (GPT-4.1)."""
    
    # Determine word count based on length
    word_count = {"short": 800, "medium": 1500, "long": 2500}.get(request.length, 1500)
    
    system_prompt, user_prompt = PromptTemplates.get_blog_prompt(
        topic=request.topic,
        target_audience=request.target_audience or "general audience",
        keywords=request.keywords or [],
        tone=request.tone or "professional",
        word_count=word_count,
        goal=request.additional_instructions or "educate and engage",
    )
    
    logger.info(f"Generating blog content: {request.topic}")
    ai_response = await ai_generator.generate(
        task_type="blog_content",  # Tier 2: Creative
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=4000,
    )
    
    if not ai_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {ai_response.error}"
        )
    
    blog_data = ai_response.as_json
    if not blog_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse blog content"
        )
    
    # Build full article content
    sections = blog_data.get("sections", [])
    full_content = blog_data.get("introduction", "") + "\n\n"
    for section in sections:
        full_content += f"## {section.get('heading', '')}\n\n"
        full_content += section.get("content", "").replace("\\n", "\n") + "\n\n"
    full_content += blog_data.get("conclusion", "")
    
    return ContentGenerateResponse(
        variations=[
            ContentVariation(
                id=f"content-{uuid4()}",
                content=full_content,
                title=blog_data.get("title", request.topic),
                meta_description=blog_data.get("meta_description"),
                call_to_action=blog_data.get("conclusion", "").split(".")[-2] if blog_data.get("conclusion") else None,
                estimated_engagement=blog_data.get("estimated_read_time", "5 min read"),
            )
        ],
        metadata={
            "content_type": "blog",
            "word_count": len(full_content.split()),
            "keywords_used": blog_data.get("keywords_used", []),
            "ai_model": ai_response.model_used,
            "ai_tier": ai_response.tier.value,
            "ai_cost": ai_response.cost_estimate,
        }
    )


async def _generate_social_content(
    request: ContentGenerateRequest,
    variations: int
) -> ContentGenerateResponse:
    """Generate social media content using Tier 3 (Llama - FREE)."""
    
    system_prompt, user_prompt = PromptTemplates.get_social_prompt(
        platform=request.platform or "twitter",
        topic=request.topic,
        goal=request.additional_instructions or "engagement",
        brand_voice=request.tone or "professional",
        count=variations,
    )
    
    logger.info(f"Generating social content for {request.platform}: {request.topic}")
    ai_response = await ai_generator.generate(
        task_type="social_post",  # Tier 3: Standard (FREE)
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.8,
        max_tokens=2000,
    )
    
    if not ai_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {ai_response.error}"
        )
    
    social_data = ai_response.as_json
    if not social_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse social content"
        )
    
    content_variations = []
    for post in social_data.get("posts", []):
        content_variations.append(ContentVariation(
            id=f"content-{uuid4()}",
            content=post.get("content", ""),
            hashtags=post.get("hashtags", []),
            call_to_action=post.get("engagement_hook"),
            estimated_engagement=post.get("best_posting_time"),
        ))
    
    return ContentGenerateResponse(
        variations=content_variations,
        metadata={
            "content_type": "social_post",
            "platform": request.platform,
            "ai_model": ai_response.model_used,
            "ai_tier": ai_response.tier.value,
            "ai_cost": ai_response.cost_estimate,  # Should be $0 for Llama
        }
    )


async def _generate_email_content(
    request: ContentGenerateRequest,
    variations: int
) -> ContentGenerateResponse:
    """Generate email content using Tier 3 (Llama - FREE)."""
    
    system_prompt, user_prompt = PromptTemplates.get_email_prompt(
        email_type=request.platform or "newsletter",
        goal=request.additional_instructions or "engagement",
        audience=request.target_audience or "subscribers",
        key_message=request.topic,
    )
    
    logger.info(f"Generating email content: {request.topic}")
    ai_response = await ai_generator.generate(
        task_type="email",  # Tier 3: Standard (FREE)
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.7,
        max_tokens=2000,
    )
    
    if not ai_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {ai_response.error}"
        )
    
    email_data = ai_response.as_json
    if not email_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse email content"
        )
    
    # Build full email
    full_content = f"Subject: {email_data.get('subject_line', '')}\n\n"
    full_content += email_data.get("body", "").replace("\\n", "\n")
    if email_data.get("ps_line"):
        full_content += f"\n\nP.S. {email_data.get('ps_line')}"
    
    return ContentGenerateResponse(
        variations=[
            ContentVariation(
                id=f"content-{uuid4()}",
                content=full_content,
                title=email_data.get("subject_line"),
                call_to_action=email_data.get("cta_text"),
            )
        ],
        metadata={
            "content_type": "email",
            "subject_variations": email_data.get("subject_variations", []),
            "preview_text": email_data.get("preview_text"),
            "ai_model": ai_response.model_used,
            "ai_tier": ai_response.tier.value,
            "ai_cost": ai_response.cost_estimate,  # Should be $0 for Llama
        }
    )


async def _generate_ad_content(
    request: ContentGenerateRequest,
    variations: int
) -> ContentGenerateResponse:
    """Generate ad copy using Tier 2 (GPT-4.1)."""
    
    system_prompt, user_prompt = PromptTemplates.get_ad_prompt(
        product_name=request.topic,
        product_description=request.additional_instructions or request.topic,
        target_audience=request.target_audience or "general audience",
        platform=request.platform or "meta",
        ad_type="feed",
        goal="conversion",
        count=variations,
    )
    
    logger.info(f"Generating ad content: {request.topic}")
    ai_response = await ai_generator.generate(
        task_type="ad_copy",  # Tier 2: Creative
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.85,
        max_tokens=2500,
    )
    
    if not ai_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content generation failed: {ai_response.error}"
        )
    
    ad_data = ai_response.as_json
    if not ad_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse ad content"
        )
    
    content_variations = []
    for ad in ad_data.get("variants", []):
        content_variations.append(ContentVariation(
            id=f"content-{uuid4()}",
            content=f"{ad.get('headline', '')}\n\n{ad.get('description', '')}",
            title=ad.get("headline"),
            call_to_action=ad.get("cta"),
            estimated_engagement=f"Predicted CTR: {ad.get('predicted_ctr', 'N/A')}%",
        ))
    
    return ContentGenerateResponse(
        variations=content_variations,
        metadata={
            "content_type": "ad_copy",
            "platform": request.platform,
            "ai_model": ai_response.model_used,
            "ai_tier": ai_response.tier.value,
            "ai_cost": ai_response.cost_estimate,
        }
    )


@router.post("/ideas", response_model=IdeaGenerateResponse)
async def generate_ideas(
    request: IdeaGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate content ideas using AI.
    Uses Tier 3 (Llama - FREE) for idea brainstorming.
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
    
    # Build prompt for idea generation
    system_prompt = """You are a content strategist. Generate creative, actionable content ideas.
Output ONLY valid JSON with this structure:
{"ideas": [{"title": "Idea title", "description": "Brief description", "content_type": "blog/social/video/email", "suggested_platforms": ["platform1", "platform2"], "trending_score": 0.8}]}"""
    
    user_prompt = f"""Generate {request.count} content ideas for:
Topic: {request.topic or 'general marketing'}
Industry: {request.industry or 'general'}
Target Audience: {request.target_audience or 'business professionals'}

Include a mix of content types (blog, social, video, email) and platforms."""
    
    ai_response = await ai_generator.generate(
        task_type="summarize",  # Tier 3: Standard (FREE)
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.9,  # High creativity for brainstorming
        max_tokens=2000,
    )
    
    if not ai_response.success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Idea generation failed: {ai_response.error}"
        )
    
    ideas_data = ai_response.as_json
    if not ideas_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse ideas"
        )
    
    ideas = []
    for idea in ideas_data.get("ideas", []):
        ideas.append(ContentIdea(
            id=f"idea-{uuid4()}",
            title=idea.get("title", "Untitled"),
            description=idea.get("description", ""),
            content_type=idea.get("content_type", "blog"),
            suggested_platforms=idea.get("suggested_platforms", ["linkedin"]),
            trending_score=idea.get("trending_score"),
        ))
    
    return IdeaGenerateResponse(ideas=ideas)


@router.get("/types")
async def get_content_types(
    current_user: User = Depends(get_current_user)
):
    """Get available content types and their details."""
    return {
        "types": [
            {
                "id": "social_post",
                "name": "Social Media Post",
                "description": "Short-form content for social platforms",
                "platforms": ["twitter", "linkedin", "facebook", "instagram"],
                "ai_tier": "standard",
                "cost": "FREE",
            },
            {
                "id": "blog",
                "name": "Blog Article",
                "description": "Long-form SEO-optimized content",
                "platforms": ["website", "medium", "linkedin"],
                "ai_tier": "creative",
                "cost": "~$0.02-0.05 per article",
            },
            {
                "id": "email",
                "name": "Email Newsletter",
                "description": "Email marketing content with subject lines",
                "platforms": ["email"],
                "ai_tier": "standard",
                "cost": "FREE",
            },
            {
                "id": "ad_copy",
                "name": "Ad Copy",
                "description": "Advertising copy for paid campaigns",
                "platforms": ["google", "meta", "linkedin", "tiktok"],
                "ai_tier": "creative",
                "cost": "~$0.01-0.03 per set",
            },
            {
                "id": "landing_page",
                "name": "Landing Page Copy",
                "description": "Conversion-focused website copy",
                "platforms": ["website"],
                "ai_tier": "creative",
                "cost": "~$0.03-0.05 per page",
            },
        ]
    }
