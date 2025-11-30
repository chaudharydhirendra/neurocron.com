"""
NeuroCron BrandVault API
Asset library with versioning, tagging, and organization
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetFolder, AssetTag, AssetTagMapping, BrandGuideline

router = APIRouter()


# === Schemas ===

class AssetCreate(BaseModel):
    name: str
    description: Optional[str] = None
    folder_id: Optional[UUID] = None
    asset_type: str = "other"


class FolderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    color: Optional[str] = None


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class BrandGuidelineUpdate(BaseModel):
    brand_name: Optional[str] = None
    tagline: Optional[str] = None
    mission: Optional[str] = None
    voice_tone: Optional[str] = None
    primary_colors: Optional[List[dict]] = None
    secondary_colors: Optional[List[dict]] = None
    primary_font: Optional[str] = None
    secondary_font: Optional[str] = None


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


# === Assets ===

@router.get("/assets")
async def list_assets(
    org_id: UUID = Query(...),
    folder_id: Optional[UUID] = None,
    asset_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List assets with filtering."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = (
        select(Asset)
        .where(Asset.organization_id == org_id)
        .where(Asset.is_archived == False)
        .where(Asset.is_latest == True)
    )
    
    if folder_id:
        query = query.where(Asset.folder_id == folder_id)
    
    if asset_type:
        try:
            type_enum = AssetType(asset_type.lower())
            query = query.where(Asset.asset_type == type_enum)
        except ValueError:
            pass
    
    if search:
        query = query.where(
            or_(
                Asset.name.ilike(f"%{search}%"),
                Asset.description.ilike(f"%{search}%"),
            )
        )
    
    # Count
    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar() or 0
    
    # Get assets
    query = query.order_by(Asset.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return {
        "assets": [
            {
                "id": str(a.id),
                "name": a.name,
                "description": a.description,
                "asset_type": a.asset_type.value,
                "file_type": a.file_type,
                "file_size": a.file_size,
                "width": a.width,
                "height": a.height,
                "thumbnail_url": a.thumbnail_path,
                "public_url": a.public_url,
                "version": a.version,
                "usage_count": a.usage_count,
                "created_at": a.created_at.isoformat(),
            }
            for a in assets
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/assets")
async def create_asset(
    asset: AssetCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create asset metadata (file upload separate)."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    try:
        asset_type = AssetType(asset.asset_type.lower())
    except ValueError:
        asset_type = AssetType.OTHER
    
    new_asset = Asset(
        organization_id=org_id,
        uploaded_by=current_user.id,
        folder_id=asset.folder_id,
        name=asset.name,
        description=asset.description,
        file_name=f"{asset.name}.tmp",
        file_type="application/octet-stream",
        file_extension="tmp",
        storage_path=f"/pending/{org_id}/{asset.name}",
        asset_type=asset_type,
    )
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    
    return {
        "id": str(new_asset.id),
        "upload_url": f"/api/v1/assets/{new_asset.id}/upload",
        "message": "Asset created. Upload file to complete.",
    }


@router.get("/assets/{asset_id}")
async def get_asset(
    asset_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get asset details."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Asset)
        .where(Asset.id == asset_id)
        .where(Asset.organization_id == org_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Increment view count
    asset.view_count += 1
    await db.commit()
    
    # Get tags
    tags_result = await db.execute(
        select(AssetTag)
        .join(AssetTagMapping, AssetTag.id == AssetTagMapping.tag_id)
        .where(AssetTagMapping.asset_id == asset_id)
    )
    tags = tags_result.scalars().all()
    
    return {
        "id": str(asset.id),
        "name": asset.name,
        "description": asset.description,
        "asset_type": asset.asset_type.value,
        "file_name": asset.file_name,
        "file_type": asset.file_type,
        "file_size": asset.file_size,
        "file_extension": asset.file_extension,
        "width": asset.width,
        "height": asset.height,
        "duration": asset.duration,
        "public_url": asset.public_url,
        "thumbnail_url": asset.thumbnail_path,
        "alt_text": asset.alt_text,
        "ai_tags": asset.ai_tags,
        "ai_description": asset.ai_description,
        "version": asset.version,
        "stats": {
            "views": asset.view_count,
            "downloads": asset.download_count,
            "uses": asset.usage_count,
        },
        "tags": [{"id": str(t.id), "name": t.name, "color": t.color} for t in tags],
        "metadata": asset.file_metadata,
        "created_at": asset.created_at.isoformat(),
        "last_used_at": asset.last_used_at.isoformat() if asset.last_used_at else None,
    }


@router.delete("/assets/{asset_id}")
async def archive_asset(
    asset_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive an asset (soft delete)."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Asset)
        .where(Asset.id == asset_id)
        .where(Asset.organization_id == org_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.is_archived = True
    await db.commit()
    
    return {"message": "Asset archived"}


# === Folders ===

@router.get("/folders")
async def list_folders(
    org_id: UUID = Query(...),
    parent_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List folders."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = select(AssetFolder).where(AssetFolder.organization_id == org_id)
    
    if parent_id:
        query = query.where(AssetFolder.parent_id == parent_id)
    else:
        query = query.where(AssetFolder.parent_id == None)
    
    result = await db.execute(query.order_by(AssetFolder.name))
    folders = result.scalars().all()
    
    return {
        "folders": [
            {
                "id": str(f.id),
                "name": f.name,
                "description": f.description,
                "color": f.color,
                "asset_count": f.asset_count,
                "subfolder_count": f.subfolder_count,
                "path": f.path,
            }
            for f in folders
        ]
    }


@router.post("/folders")
async def create_folder(
    folder: FolderCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a folder."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get parent path
    path = "/"
    depth = 0
    if folder.parent_id:
        parent = await db.execute(
            select(AssetFolder).where(AssetFolder.id == folder.parent_id)
        )
        parent_folder = parent.scalar_one_or_none()
        if parent_folder:
            path = f"{parent_folder.path}{parent_folder.name}/"
            depth = parent_folder.depth + 1
    
    new_folder = AssetFolder(
        organization_id=org_id,
        parent_id=folder.parent_id,
        name=folder.name,
        description=folder.description,
        color=folder.color,
        path=path,
        depth=depth,
    )
    db.add(new_folder)
    
    # Update parent folder count
    if folder.parent_id:
        parent_result = await db.execute(
            select(AssetFolder).where(AssetFolder.id == folder.parent_id)
        )
        parent = parent_result.scalar_one_or_none()
        if parent:
            parent.subfolder_count += 1
    
    await db.commit()
    await db.refresh(new_folder)
    
    return {"id": str(new_folder.id), "message": "Folder created"}


# === Tags ===

@router.get("/tags")
async def list_tags(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tags."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(AssetTag)
        .where(AssetTag.organization_id == org_id)
        .order_by(AssetTag.usage_count.desc())
    )
    tags = result.scalars().all()
    
    return {
        "tags": [
            {
                "id": str(t.id),
                "name": t.name,
                "color": t.color,
                "usage_count": t.usage_count,
            }
            for t in tags
        ]
    }


@router.post("/tags")
async def create_tag(
    tag: TagCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a tag."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_tag = AssetTag(
        organization_id=org_id,
        name=tag.name,
        color=tag.color,
    )
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)
    
    return {"id": str(new_tag.id), "message": "Tag created"}


@router.post("/assets/{asset_id}/tags/{tag_id}")
async def add_tag_to_asset(
    asset_id: UUID,
    tag_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a tag to an asset."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    mapping = AssetTagMapping(asset_id=asset_id, tag_id=tag_id)
    db.add(mapping)
    
    # Update tag usage count
    tag = await db.execute(select(AssetTag).where(AssetTag.id == tag_id))
    tag_obj = tag.scalar_one_or_none()
    if tag_obj:
        tag_obj.usage_count += 1
    
    await db.commit()
    
    return {"message": "Tag added"}


# === Brand Guidelines ===

@router.get("/brand-guidelines")
async def get_brand_guidelines(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get brand guidelines."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(BrandGuideline).where(BrandGuideline.organization_id == org_id)
    )
    guidelines = result.scalar_one_or_none()
    
    if not guidelines:
        return {"guidelines": None}
    
    return {
        "guidelines": {
            "brand_name": guidelines.brand_name,
            "tagline": guidelines.tagline,
            "mission": guidelines.mission,
            "voice_tone": guidelines.voice_tone,
            "colors": {
                "primary": guidelines.primary_colors,
                "secondary": guidelines.secondary_colors,
            },
            "typography": {
                "primary_font": guidelines.primary_font,
                "secondary_font": guidelines.secondary_font,
                "guidelines": guidelines.font_guidelines,
            },
            "logo_usage": guidelines.logo_usage_rules,
            "dos": guidelines.do_guidelines,
            "donts": guidelines.dont_guidelines,
            "is_published": guidelines.is_published,
        }
    }


@router.put("/brand-guidelines")
async def update_brand_guidelines(
    update: BrandGuidelineUpdate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update brand guidelines."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(BrandGuideline).where(BrandGuideline.organization_id == org_id)
    )
    guidelines = result.scalar_one_or_none()
    
    if not guidelines:
        guidelines = BrandGuideline(
            organization_id=org_id,
            brand_name=update.brand_name or "My Brand",
        )
        db.add(guidelines)
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(guidelines, key, value)
    
    await db.commit()
    
    return {"message": "Brand guidelines updated"}

