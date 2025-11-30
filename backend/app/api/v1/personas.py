"""
NeuroCron AudienceGenome API
AI-powered customer persona and segmentation engine

AI Tier Used: Tier 2 - GPT-4.1 (best creative/persona generation)
"""

from typing import List, Optional
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.persona import Persona, AudienceSegment
from app.services.ai import ai_generator, PromptTemplates

logger = logging.getLogger(__name__)
router = APIRouter()


class PersonaGenerateRequest(BaseModel):
    """Request to generate personas"""
    business_type: str = Field(..., description="Type of business")
    target_market: str = Field(..., description="Target market description")
    products_services: str = Field(..., description="Products or services offered")
    count: int = Field(3, ge=1, le=5, description="Number of personas to generate")
    price_point: Optional[str] = Field("mid-range", description="Price positioning")


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
    
    Uses Tier 2 (GPT-4.1) for best persona/creative generation.
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
    
    # Get prompts for persona generation
    system_prompt, user_prompt = PromptTemplates.get_persona_prompt(
        business_type=request.business_type,
        target_market=request.target_market,
        products_services=request.products_services,
        count=request.count,
        price_point=request.price_point or "mid-range",
    )
    
    # Generate personas using AI (Tier 2: Creative - GPT-4.1)
    logger.info(f"Generating {request.count} personas using AI")
    ai_response = await ai_generator.generate(
        task_type="persona",
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.8,  # Creative temperature for varied personas
        max_tokens=4000,
    )
    
    if not ai_response.success:
        logger.error(f"AI generation failed: {ai_response.error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Persona generation failed: {ai_response.error}"
        )
    
    # Parse the AI response
    personas_data = ai_response.as_json
    if not personas_data:
        logger.error("Failed to parse AI response as JSON")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse personas response"
        )
    
    # Log cost for monitoring
    logger.info(
        f"Personas generated: model={ai_response.model_used}, "
        f"tokens_in={ai_response.tokens_in}, tokens_out={ai_response.tokens_out}, "
        f"cost=${ai_response.cost_estimate:.4f}"
    )
    
    # Save to database
    saved_personas = []
    for p_data in personas_data.get("personas", []):
        persona = Persona(
            organization_id=org_id,
            name=p_data.get("name", "Unknown Persona"),
            age_range=p_data.get("age_range"),
            occupation=p_data.get("occupation"),
            income_level=p_data.get("income_level"),
            location=p_data.get("location"),
            bio=p_data.get("bio"),
            goals=p_data.get("goals", []),
            pain_points=p_data.get("pain_points", []),
            motivations=p_data.get("motivations", []),
            objections=p_data.get("objections", []),
            preferred_channels=p_data.get("preferred_channels", []),
            buying_triggers=p_data.get("buying_triggers", []),
            content_preferences=p_data.get("content_preferences", []),
            brand_affinity=p_data.get("brand_affinity", []),
            psychographic_profile=p_data.get("psychographic_profile"),
            generation_context={
                "business_type": request.business_type,
                "target_market": request.target_market,
                "products_services": request.products_services,
                "ai_model": ai_response.model_used,
                "ai_cost": ai_response.cost_estimate,
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
        targeting_recommendations=personas_data.get("targeting_recommendations", [
            "Focus on the primary persona's preferred channels",
            "Create content addressing specific pain points",
        ]),
        content_strategy=personas_data.get("content_strategy", 
            "Focus on solving specific pain points with actionable content."
        )
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
    """Get AI-generated audience insights based on existing personas."""
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
    
    # Get existing personas for this org
    result = await db.execute(
        select(Persona)
        .where(Persona.organization_id == org_id)
        .limit(10)
    )
    personas = result.scalars().all()
    
    # Aggregate insights from personas
    all_channels = []
    all_content_prefs = []
    for p in personas:
        all_channels.extend(p.preferred_channels or [])
        all_content_prefs.extend(p.content_preferences or [])
    
    # Count frequencies
    from collections import Counter
    channel_counts = Counter(all_channels)
    content_counts = Counter(all_content_prefs)
    
    return {
        "total_personas": len(personas),
        "top_channels": [
            {"channel": ch, "count": cnt, "percentage": round(cnt/len(all_channels)*100) if all_channels else 0}
            for ch, cnt in channel_counts.most_common(5)
        ] if all_channels else [],
        "top_content_preferences": [
            {"type": ct, "count": cnt}
            for ct, cnt in content_counts.most_common(5)
        ] if all_content_prefs else [],
        "engagement_patterns": {
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "best_times": ["9-11 AM", "1-3 PM", "7-9 PM"],
        },
        "recommendations": [
            "Focus content on the most preferred channels",
            "Create varied content formats to match preferences",
            "Schedule posts during peak engagement times",
        ] if personas else [
            "Generate personas to get personalized insights",
            "Connect analytics to see real engagement data",
        ],
    }
