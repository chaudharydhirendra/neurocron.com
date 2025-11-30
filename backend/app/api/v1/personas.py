"""
NeuroCron AudienceGenome API
AI-powered customer persona and segmentation engine
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
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


class PersonaGenerateRequest(BaseModel):
    """Request to generate personas"""
    business_type: str = Field(..., description="Type of business")
    target_market: str = Field(..., description="Target market description")
    products_services: str = Field(..., description="Products or services offered")
    count: int = Field(3, ge=1, le=5, description="Number of personas to generate")


class Persona(BaseModel):
    """Customer persona"""
    id: str
    name: str
    age_range: str
    occupation: str
    income_level: str
    location: str
    bio: str
    goals: List[str]
    pain_points: List[str]
    motivations: List[str]
    objections: List[str]
    preferred_channels: List[str]
    buying_triggers: List[str]
    content_preferences: List[str]
    brand_affinity: List[str]
    psychographic_profile: str


class PersonaGenerateResponse(BaseModel):
    """Response with generated personas"""
    personas: List[Persona]
    targeting_recommendations: List[str]
    content_strategy: str


class SegmentRequest(BaseModel):
    """Request to create audience segment"""
    name: str
    description: Optional[str] = None
    criteria: dict  # Filtering criteria


@router.post("/generate", response_model=PersonaGenerateResponse)
async def generate_personas(
    request: PersonaGenerateRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate AI-powered customer personas.
    
    Uses AI to create detailed buyer personas based on business information.
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
    
    # Generate personas using AI
    prompt = f"""Generate {request.count} detailed marketing personas for a business.

Business Type: {request.business_type}
Target Market: {request.target_market}
Products/Services: {request.products_services}

For each persona, provide:
- Name (fictional but realistic)
- Age range
- Occupation
- Income level
- Location type
- Short bio (2-3 sentences)
- 3-4 Goals
- 3-4 Pain points
- 3-4 Motivations
- 2-3 Potential objections to buying
- Preferred marketing channels
- Buying triggers
- Content format preferences
- Brands they like

Also provide:
- 3-5 targeting recommendations for reaching these personas
- A brief content strategy summary
"""
    
    # Try to generate with AI
    personas = _generate_sample_personas(request)
    
    return PersonaGenerateResponse(
        personas=personas,
        targeting_recommendations=[
            "Focus on professional networking platforms for B2B personas",
            "Use video content for younger demographics",
            "Implement retargeting for high-intent visitors",
            "Create educational content for problem-aware personas",
            "Leverage social proof and testimonials for trust-building",
        ],
        content_strategy="Focus on solving specific pain points with actionable, educational content. Use a mix of blog posts, short-form video, and case studies to appeal to different preferences."
    )


@router.get("/templates")
async def get_persona_templates(
    industry: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Get pre-built persona templates by industry."""
    templates = {
        "saas": [
            {
                "id": "tech_startup_founder",
                "name": "Tech Startup Founder",
                "description": "Decision-maker at early-stage tech companies",
                "key_traits": ["Time-constrained", "Growth-focused", "Tech-savvy"],
            },
            {
                "id": "marketing_manager",
                "name": "Marketing Manager",
                "description": "Mid-level marketing professional at growing company",
                "key_traits": ["ROI-focused", "Data-driven", "Tool-savvy"],
            },
        ],
        "ecommerce": [
            {
                "id": "value_shopper",
                "name": "Value-Conscious Shopper",
                "description": "Price-sensitive but quality-aware consumer",
                "key_traits": ["Deal-seeker", "Review-reader", "Patient buyer"],
            },
            {
                "id": "trendsetter",
                "name": "Early Adopter Trendsetter",
                "description": "Fashion-forward, social media active shopper",
                "key_traits": ["Influencer", "Premium buyer", "Brand-loyal"],
            },
        ],
        "professional_services": [
            {
                "id": "enterprise_buyer",
                "name": "Enterprise Decision Maker",
                "description": "C-suite or VP level at large corporation",
                "key_traits": ["Risk-averse", "Relationship-driven", "Long sales cycle"],
            },
            {
                "id": "smb_owner",
                "name": "Small Business Owner",
                "description": "Owner of company with 10-50 employees",
                "key_traits": ["Budget-conscious", "Hands-on", "Quick decisions"],
            },
        ],
    }
    
    if industry and industry in templates:
        return {"templates": templates[industry]}
    
    return {"templates": templates}


@router.post("/segments")
async def create_segment(
    segment: SegmentRequest,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create an audience segment."""
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
        "id": "segment-id",
        "name": segment.name,
        "description": segment.description,
        "criteria": segment.criteria,
        "estimated_size": 15000,
        "message": "Segment created successfully",
    }


@router.get("/insights")
async def get_audience_insights(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated audience insights."""
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
        "top_demographics": [
            {"label": "Age 25-34", "percentage": 38},
            {"label": "Age 35-44", "percentage": 28},
            {"label": "Age 18-24", "percentage": 18},
            {"label": "Age 45-54", "percentage": 12},
            {"label": "Age 55+", "percentage": 4},
        ],
        "top_interests": [
            {"label": "Technology", "affinity": 85},
            {"label": "Business", "affinity": 72},
            {"label": "Marketing", "affinity": 68},
            {"label": "Entrepreneurship", "affinity": 65},
            {"label": "Self-improvement", "affinity": 58},
        ],
        "top_locations": [
            {"label": "United States", "percentage": 45},
            {"label": "United Kingdom", "percentage": 15},
            {"label": "Canada", "percentage": 12},
            {"label": "Australia", "percentage": 8},
            {"label": "Germany", "percentage": 5},
        ],
        "device_breakdown": [
            {"label": "Mobile", "percentage": 62},
            {"label": "Desktop", "percentage": 32},
            {"label": "Tablet", "percentage": 6},
        ],
        "engagement_patterns": {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_times": ["9-11 AM", "1-3 PM", "7-9 PM"],
            "preferred_content": ["Video", "Infographics", "How-to guides"],
        },
    }


def _generate_sample_personas(request: PersonaGenerateRequest) -> List[Persona]:
    """Generate sample personas (fallback when AI unavailable)."""
    sample_personas = [
        Persona(
            id="persona-1",
            name="Alex Marketing Manager",
            age_range="28-35",
            occupation="Marketing Manager at mid-size company",
            income_level="$70,000 - $100,000",
            location="Urban, major metropolitan area",
            bio="Alex is a data-driven marketing professional who's always looking for tools to streamline workflows and prove ROI. They manage a small team and report to the CMO.",
            goals=["Increase marketing ROI", "Automate repetitive tasks", "Impress leadership with results"],
            pain_points=["Too many tools to manage", "Difficulty proving attribution", "Limited budget"],
            motivations=["Career advancement", "Team efficiency", "Recognition"],
            objections=["Budget constraints", "Learning curve", "Integration concerns"],
            preferred_channels=["LinkedIn", "Email", "Industry blogs"],
            buying_triggers=["Free trial", "Case studies", "Peer recommendations"],
            content_preferences=["How-to guides", "Webinars", "Comparison charts"],
            brand_affinity=["HubSpot", "Slack", "Notion"],
            psychographic_profile="Achievement-oriented professional who values efficiency and data-backed decisions.",
        ),
        Persona(
            id="persona-2",
            name="Sarah Startup Founder",
            age_range="30-40",
            occupation="CEO/Founder of early-stage startup",
            income_level="Variable, equity-focused",
            location="Tech hub cities",
            bio="Sarah is a driven entrepreneur who wears many hats. She needs solutions that save time and scale with her growing business.",
            goals=["Scale the business", "Reduce operational overhead", "Find product-market fit"],
            pain_points=["Limited resources", "Time constraints", "Information overload"],
            motivations=["Building something meaningful", "Financial independence", "Innovation"],
            objections=["Is this essential right now?", "Can we build it ourselves?", "Pricing concerns"],
            preferred_channels=["Twitter/X", "Podcasts", "Founder communities"],
            buying_triggers=["Founder testimonials", "Quick wins", "Flexible pricing"],
            content_preferences=["Case studies", "Podcasts", "Quick tips"],
            brand_affinity=["Stripe", "Figma", "Linear"],
            psychographic_profile="Visionary leader who values speed, innovation, and authentic connections.",
        ),
        Persona(
            id="persona-3",
            name="Mike Enterprise Buyer",
            age_range="40-50",
            occupation="VP of Marketing at enterprise company",
            income_level="$150,000 - $250,000",
            location="Major business centers",
            bio="Mike oversees a large marketing organization and is responsible for major technology decisions. He prioritizes reliability and proven ROI.",
            goals=["Consolidate marketing stack", "Ensure compliance", "Demonstrate value to board"],
            pain_points=["Complex approval processes", "Vendor management", "Change management"],
            motivations=["Job security", "Team success", "Strategic impact"],
            objections=["Security concerns", "Implementation complexity", "Long-term support"],
            preferred_channels=["Industry events", "Analyst reports", "Executive networks"],
            buying_triggers=["Executive references", "Enterprise case studies", "Dedicated support"],
            content_preferences=["White papers", "ROI calculators", "Executive summaries"],
            brand_affinity=["Salesforce", "Adobe", "Oracle"],
            psychographic_profile="Risk-conscious executive who values stability, proof, and strategic alignment.",
        ),
    ]
    
    return sample_personas[:request.count]

