"""
NeuroCron GlobalReach API
Multi-language content localization
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.localization import TranslationProject, TranslationItem, Translation, LocaleSettings

router = APIRouter()


# === Schemas ===

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    source_language: str = "en"
    target_languages: List[str]
    content_type: str = "marketing"


class TranslationItemCreate(BaseModel):
    item_key: str
    source_content: str
    context: Optional[str] = None
    item_type: str = "text"


class TranslateRequest(BaseModel):
    target_language: str
    use_ai: bool = True


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ru": "Russian",
}


# === Projects ===

@router.get("/projects")
async def list_projects(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List translation projects."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(TranslationProject)
        .where(TranslationProject.organization_id == org_id)
        .order_by(TranslationProject.created_at.desc())
    )
    projects = result.scalars().all()
    
    return {
        "projects": [
            {
                "id": str(p.id),
                "name": p.name,
                "source_language": p.source_language,
                "target_languages": p.target_languages,
                "content_type": p.content_type,
                "total_items": p.total_items,
                "progress": p.progress,
                "status": p.status,
            }
            for p in projects
        ]
    }


@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a translation project."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_project = TranslationProject(
        organization_id=org_id,
        name=project.name,
        description=project.description,
        source_language=project.source_language,
        target_languages=project.target_languages,
        content_type=project.content_type,
    )
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    return {"id": str(new_project.id), "message": "Project created"}


@router.post("/projects/{project_id}/items")
async def add_translation_item(
    project_id: UUID,
    item: TranslationItemCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an item to translate."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get project
    result = await db.execute(
        select(TranslationProject)
        .where(TranslationProject.id == project_id)
        .where(TranslationProject.organization_id == org_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_item = TranslationItem(
        project_id=project_id,
        item_key=item.item_key,
        item_type=item.item_type,
        source_content=item.source_content,
        context=item.context,
        source_language=project.source_language,
        word_count=len(item.source_content.split()),
        char_count=len(item.source_content),
    )
    db.add(new_item)
    
    # Update project stats
    project.total_items += 1
    
    await db.commit()
    await db.refresh(new_item)
    
    return {"id": str(new_item.id), "message": "Item added"}


@router.post("/items/{item_id}/translate")
async def translate_item(
    item_id: UUID,
    request: TranslateRequest,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Translate an item to target language."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(TranslationItem).where(TranslationItem.id == item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Check for existing translation
    existing = await db.execute(
        select(Translation)
        .where(Translation.item_id == item_id)
        .where(Translation.target_language == request.target_language)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Translation already exists")
    
    # In production, call AI translation service
    # For now, simulate with placeholder
    translated_content = f"[{request.target_language.upper()}] {item.source_content}"
    
    new_translation = Translation(
        item_id=item_id,
        target_language=request.target_language,
        translated_content=translated_content,
        translation_method="ai" if request.use_ai else "human",
        quality_score=85.0,
    )
    db.add(new_translation)
    await db.commit()
    
    return {
        "translation_id": str(new_translation.id),
        "translated_content": translated_content,
        "method": new_translation.translation_method,
    }


@router.get("/languages")
async def list_supported_languages():
    """Get list of supported languages."""
    return {
        "languages": [
            {"code": code, "name": name}
            for code, name in SUPPORTED_LANGUAGES.items()
        ]
    }


# === Locale Settings ===

@router.get("/locales")
async def list_locales(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List organization locales."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(LocaleSettings)
        .where(LocaleSettings.organization_id == org_id)
        .where(LocaleSettings.is_active == True)
    )
    locales = result.scalars().all()
    
    return {
        "locales": [
            {
                "locale_code": l.locale_code,
                "display_name": l.display_name,
                "native_name": l.native_name,
                "currency_code": l.currency_code,
                "date_format": l.date_format,
                "is_default": l.is_default,
            }
            for l in locales
        ]
    }

