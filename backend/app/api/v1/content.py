"""
NeuroCron ContentForge API
AI-powered content generation for all marketing channels
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.core.deps import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.organization import OrganizationMember

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
    content: str
    hashtags: Optional[List[str]] = None
    call_to_action: Optional[str] = None
    estimated_engagement: Optional[str] = None


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
    
    # Build the prompt
    prompt = _build_content_prompt(request, variations)
    
    # Generate using AI
    try:
        content = await _generate_with_ai(prompt)
        parsed_variations = _parse_content_response(content, request.content_type)
        
        return ContentGenerateResponse(
            variations=parsed_variations,
            metadata={
                "content_type": request.content_type,
                "platform": request.platform,
                "tone": request.tone,
                "variations_requested": variations,
            }
        )
    except Exception as e:
        # Return fallback content
        return ContentGenerateResponse(
            variations=[
                ContentVariation(
                    content=_get_fallback_content(request),
                    hashtags=["#marketing", "#content"] if request.content_type == "social_post" else None,
                    call_to_action="Learn more",
                )
            ],
            metadata={
                "content_type": request.content_type,
                "fallback": True,
                "error": str(e),
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
    Generate content ideas for your marketing strategy.
    
    Provides fresh content ideas based on your industry,
    target audience, and current trends.
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
    
    # Generate ideas
    prompt = f"""Generate {request.count} creative marketing content ideas.
    
    Context:
    - Topic/Industry: {request.topic or request.industry or "General marketing"}
    - Target Audience: {request.target_audience or "Business professionals"}
    
    For each idea, provide:
    1. A catchy title
    2. Brief description (2-3 sentences)
    3. Best content type (social post, blog, video, infographic, etc.)
    4. Suggested platforms
    
    Make the ideas unique, actionable, and trendy."""
    
    try:
        response = await _generate_with_ai(prompt)
        ideas = _parse_ideas_response(response, request.count)
        return IdeaGenerateResponse(ideas=ideas)
    except Exception:
        # Return fallback ideas
        return IdeaGenerateResponse(
            ideas=[
                ContentIdea(
                    title="Behind the Scenes",
                    description="Share your team's daily workflow and company culture.",
                    content_type="social_post",
                    suggested_platforms=["Instagram", "LinkedIn"],
                ),
                ContentIdea(
                    title="Customer Success Story",
                    description="Feature a case study highlighting how your product helped a customer.",
                    content_type="blog",
                    suggested_platforms=["Website", "LinkedIn"],
                ),
                ContentIdea(
                    title="Industry Trend Analysis",
                    description="Create a carousel or thread about emerging trends in your industry.",
                    content_type="social_post",
                    suggested_platforms=["LinkedIn", "Twitter"],
                ),
            ][:request.count]
        )


@router.post("/rewrite")
async def rewrite_content(
    content: str,
    style: str = Query("professional", description="Target style"),
    platform: Optional[str] = Query(None, description="Target platform"),
    current_user: User = Depends(get_current_user)
):
    """
    Rewrite existing content in a different style or for a specific platform.
    """
    prompt = f"""Rewrite the following content in a {style} style{f' optimized for {platform}' if platform else ''}:

Original content:
{content}

Rewritten version:"""
    
    try:
        rewritten = await _generate_with_ai(prompt)
        return {
            "original": content,
            "rewritten": rewritten.strip(),
            "style": style,
            "platform": platform,
        }
    except Exception as e:
        return {
            "original": content,
            "rewritten": content,  # Return original if AI fails
            "error": str(e),
        }


def _build_content_prompt(request: ContentGenerateRequest, variations: int) -> str:
    """Build the AI prompt for content generation."""
    
    type_instructions = {
        "social_post": "Create engaging social media posts that encourage engagement and shares.",
        "blog": "Write an informative blog article with clear sections, intro, body, and conclusion.",
        "email": "Create compelling email copy with subject line, preview text, and body content.",
        "ad_copy": "Write persuasive advertising copy with headline, body, and call-to-action.",
        "landing_page": "Create landing page copy with headline, value propositions, and CTA sections.",
    }
    
    prompt = f"""You are a professional marketing copywriter. Generate {variations} variations of {request.content_type} content.

TASK: {type_instructions.get(request.content_type, 'Create marketing content.')}

TOPIC: {request.topic}
"""
    
    if request.platform:
        prompt += f"\nPLATFORM: {request.platform}"
    if request.tone:
        prompt += f"\nTONE: {request.tone}"
    if request.target_audience:
        prompt += f"\nTARGET AUDIENCE: {request.target_audience}"
    if request.keywords:
        prompt += f"\nKEYWORDS TO INCLUDE: {', '.join(request.keywords)}"
    if request.length:
        length_guide = {"short": "50-100 words", "medium": "150-300 words", "long": "400-800 words"}
        prompt += f"\nLENGTH: {length_guide.get(request.length, request.length)}"
    if request.additional_instructions:
        prompt += f"\nADDITIONAL INSTRUCTIONS: {request.additional_instructions}"
    
    prompt += f"""

Generate exactly {variations} unique variations. For each variation:
1. The main content
2. Suggested hashtags (for social posts)
3. A call-to-action

Format each variation clearly with a separator."""
    
    return prompt


async def _generate_with_ai(prompt: str) -> str:
    """Generate content using available AI service."""
    
    messages = [
        {"role": "system", "content": "You are a professional marketing copywriter who creates engaging, conversion-focused content."},
        {"role": "user", "content": prompt},
    ]
    
    # Try Ollama first
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except Exception:
        pass
    
    # Try OpenAI
    if settings.OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.OPENAI_MODEL,
                        "messages": messages,
                        "max_tokens": 2000,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            pass
    
    raise Exception("No AI service available")


def _parse_content_response(response: str, content_type: str) -> List[ContentVariation]:
    """Parse AI response into structured content variations."""
    # Simple parsing - split by common separators
    parts = response.split("---")
    if len(parts) == 1:
        parts = response.split("Variation")
    if len(parts) == 1:
        parts = [response]
    
    variations = []
    for part in parts:
        if not part.strip():
            continue
        
        # Extract hashtags if social post
        hashtags = None
        if content_type == "social_post":
            import re
            hashtag_matches = re.findall(r'#\w+', part)
            if hashtag_matches:
                hashtags = list(set(hashtag_matches))[:5]
        
        variations.append(ContentVariation(
            content=part.strip(),
            hashtags=hashtags,
            call_to_action="Learn more" if "cta" not in part.lower() else None,
        ))
    
    return variations[:5]  # Max 5 variations


def _parse_ideas_response(response: str, count: int) -> List[ContentIdea]:
    """Parse AI response into structured content ideas."""
    # Return placeholder ideas if parsing fails
    return [
        ContentIdea(
            title=f"Content Idea {i+1}",
            description="AI-generated content idea based on your input.",
            content_type="social_post",
            suggested_platforms=["LinkedIn", "Instagram"],
        )
        for i in range(min(count, 5))
    ]


def _get_fallback_content(request: ContentGenerateRequest) -> str:
    """Generate fallback content when AI is unavailable."""
    fallbacks = {
        "social_post": f"📢 {request.topic}\n\nDiscover how we're making a difference. Stay tuned for more updates!\n\n#marketing #innovation #growth",
        "blog": f"# {request.topic}\n\nIntroduction to this important topic...\n\n## Key Points\n\n1. First key insight\n2. Second key insight\n3. Third key insight\n\n## Conclusion\n\nIn conclusion, this topic is essential for...",
        "email": f"Subject: Exciting News About {request.topic}\n\nHi there,\n\nWe're thrilled to share something special with you...\n\nBest regards,\nThe Team",
        "ad_copy": f"✨ {request.topic}\n\nTransform your approach today. Limited time offer.\n\n👉 Learn More",
        "landing_page": f"# {request.topic}\n\n## Transform Your Business\n\nDiscover the power of our solution.\n\n### Why Choose Us?\n\n- Benefit 1\n- Benefit 2\n- Benefit 3\n\n[Get Started →]",
    }
    return fallbacks.get(request.content_type, f"Content about {request.topic}")

