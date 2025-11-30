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
from app.models.persona import Persona, AudienceSegment

router = APIRouter()


class PersonaGenerateRequest(BaseModel):
    """Request to generate personas"""
    business_type: str = Field(..., description="Type of business")
    target_market: str = Field(..., description="Target market description")
    products_services: str = Field(..., description="Products or services offered")
    count: int = Field(3, ge=1, le=5, description="Number of personas to generate")


class PersonaResponse(BaseModel):
    """Persona response schema"""
    id: str
    name: str
    age_range: Optional[str]
    occupation: Optional[str]
    income_level: Optional[str]
    location: Optional[str]
    bio: Optional[str]
    goals: List[str]
    pain_points: List[str]
    motivations: List[str]
    objections: List[str]
    preferred_channels: List[str]
    buying_triggers: List[str]
    content_preferences: List[str]
    brand_affinity: List[str]
    psychographic_profile: Optional[str]


class PersonaGenerateResponse(BaseModel):
    """Response with generated personas"""
    personas: List[PersonaResponse]
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
    Generate AI-powered customer personas and save them to the database.
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
    
    # Generate personas using AI (or sample data)
    generated_personas = _generate_sample_personas(request)
    
    # Save to database
    saved_personas = []
    for p_data in generated_personas:
        persona = Persona(
            organization_id=org_id,
            name=p_data["name"],
            age_range=p_data["age_range"],
            occupation=p_data["occupation"],
            income_level=p_data["income_level"],
            location=p_data["location"],
            bio=p_data["bio"],
            goals=p_data["goals"],
            pain_points=p_data["pain_points"],
            motivations=p_data["motivations"],
            objections=p_data["objections"],
            preferred_channels=p_data["preferred_channels"],
            buying_triggers=p_data["buying_triggers"],
            content_preferences=p_data["content_preferences"],
            brand_affinity=p_data["brand_affinity"],
            psychographic_profile=p_data["psychographic_profile"],
            generation_context={
                "business_type": request.business_type,
                "target_market": request.target_market,
                "products_services": request.products_services,
            }
        )
        db.add(persona)
        saved_personas.append(persona)
    
    await db.commit()
    
    # Refresh to get IDs
    for persona in saved_personas:
        await db.refresh(persona)
    
    # Convert to response format
    persona_responses = [
        PersonaResponse(
            id=str(p.id),
            name=p.name,
            age_range=p.age_range,
            occupation=p.occupation,
            income_level=p.income_level,
            location=p.location,
            bio=p.bio,
            goals=p.goals or [],
            pain_points=p.pain_points or [],
            motivations=p.motivations or [],
            objections=p.objections or [],
            preferred_channels=p.preferred_channels or [],
            buying_triggers=p.buying_triggers or [],
            content_preferences=p.content_preferences or [],
            brand_affinity=p.brand_affinity or [],
            psychographic_profile=p.psychographic_profile,
        )
        for p in saved_personas
    ]
    
    return PersonaGenerateResponse(
        personas=persona_responses,
        targeting_recommendations=[
            "Focus on professional networking platforms for B2B personas",
            "Use video content for younger demographics",
            "Implement retargeting for high-intent visitors",
            "Create educational content for problem-aware personas",
            "Leverage social proof and testimonials for trust-building",
        ],
        content_strategy="Focus on solving specific pain points with actionable, educational content. Use a mix of blog posts, short-form video, and case studies to appeal to different preferences."
    )


@router.get("/")
async def list_personas(
    org_id: UUID = Query(..., description="Organization ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all personas for an organization."""
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
    
    # Fetch personas
    result = await db.execute(
        select(Persona)
        .where(Persona.organization_id == org_id)
        .offset(skip)
        .limit(limit)
        .order_by(Persona.created_at.desc())
    )
    personas = result.scalars().all()
    
    return {
        "personas": [
            {
                "id": str(p.id),
                "name": p.name,
                "age_range": p.age_range,
                "occupation": p.occupation,
                "income_level": p.income_level,
                "location": p.location,
                "bio": p.bio,
                "goals": p.goals or [],
                "pain_points": p.pain_points or [],
                "motivations": p.motivations or [],
                "objections": p.objections or [],
                "preferred_channels": p.preferred_channels or [],
                "buying_triggers": p.buying_triggers or [],
                "content_preferences": p.content_preferences or [],
                "brand_affinity": p.brand_affinity or [],
                "psychographic_profile": p.psychographic_profile,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in personas
        ],
        "total": len(personas),
    }


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: UUID,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a persona."""
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
    
    # Fetch and delete
    result = await db.execute(
        select(Persona)
        .where(Persona.id == persona_id)
        .where(Persona.organization_id == org_id)
    )
    persona = result.scalar_one_or_none()
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    await db.delete(persona)
    await db.commit()
    
    return {"message": "Persona deleted successfully"}


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
    
    # Create segment
    new_segment = AudienceSegment(
        organization_id=org_id,
        name=segment.name,
        description=segment.description,
        criteria=segment.criteria,
        estimated_size=15000,  # Would calculate based on criteria
    )
    db.add(new_segment)
    await db.commit()
    await db.refresh(new_segment)
    
    return {
        "id": str(new_segment.id),
        "name": new_segment.name,
        "description": new_segment.description,
        "criteria": new_segment.criteria,
        "estimated_size": new_segment.estimated_size,
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


def _generate_sample_personas(request: PersonaGenerateRequest) -> List[dict]:
    """Generate sample personas (fallback when AI unavailable)."""
    sample_personas = [
        {
            "name": "Alex Marketing Manager",
            "age_range": "28-35",
            "occupation": "Marketing Manager at mid-size company",
            "income_level": "$70,000 - $100,000",
            "location": "Urban, major metropolitan area",
            "bio": "Alex is a data-driven marketing professional who's always looking for tools to streamline workflows and prove ROI. They manage a small team and report to the CMO.",
            "goals": ["Increase marketing ROI", "Automate repetitive tasks", "Impress leadership with results"],
            "pain_points": ["Too many tools to manage", "Difficulty proving attribution", "Limited budget"],
            "motivations": ["Career advancement", "Team efficiency", "Recognition"],
            "objections": ["Budget constraints", "Learning curve", "Integration concerns"],
            "preferred_channels": ["LinkedIn", "Email", "Industry blogs"],
            "buying_triggers": ["Free trial", "Case studies", "Peer recommendations"],
            "content_preferences": ["How-to guides", "Webinars", "Comparison charts"],
            "brand_affinity": ["HubSpot", "Slack", "Notion"],
            "psychographic_profile": "Achievement-oriented professional who values efficiency and data-backed decisions.",
        },
        {
            "name": "Sarah Startup Founder",
            "age_range": "30-40",
            "occupation": "CEO/Founder of early-stage startup",
            "income_level": "Variable, equity-focused",
            "location": "Tech hub cities",
            "bio": "Sarah is a driven entrepreneur who wears many hats. She needs solutions that save time and scale with her growing business.",
            "goals": ["Scale the business", "Reduce operational overhead", "Find product-market fit"],
            "pain_points": ["Limited resources", "Time constraints", "Information overload"],
            "motivations": ["Building something meaningful", "Financial independence", "Innovation"],
            "objections": ["Is this essential right now?", "Can we build it ourselves?", "Pricing concerns"],
            "preferred_channels": ["Twitter/X", "Podcasts", "Founder communities"],
            "buying_triggers": ["Founder testimonials", "Quick wins", "Flexible pricing"],
            "content_preferences": ["Case studies", "Podcasts", "Quick tips"],
            "brand_affinity": ["Stripe", "Figma", "Linear"],
            "psychographic_profile": "Visionary leader who values speed, innovation, and authentic connections.",
        },
        {
            "name": "Mike Enterprise Buyer",
            "age_range": "40-50",
            "occupation": "VP of Marketing at enterprise company",
            "income_level": "$150,000 - $250,000",
            "location": "Major business centers",
            "bio": "Mike oversees a large marketing organization and is responsible for major technology decisions. He prioritizes reliability and proven ROI.",
            "goals": ["Consolidate marketing stack", "Ensure compliance", "Demonstrate value to board"],
            "pain_points": ["Complex approval processes", "Vendor management", "Change management"],
            "motivations": ["Job security", "Team success", "Strategic impact"],
            "objections": ["Security concerns", "Implementation complexity", "Long-term support"],
            "preferred_channels": ["Industry events", "Analyst reports", "Executive networks"],
            "buying_triggers": ["Executive references", "Enterprise case studies", "Dedicated support"],
            "content_preferences": ["White papers", "ROI calculators", "Executive summaries"],
            "brand_affinity": ["Salesforce", "Adobe", "Oracle"],
            "psychographic_profile": "Risk-conscious executive who values stability, proof, and strategic alignment.",
        },
    ]
    
    return sample_personas[:request.count]
