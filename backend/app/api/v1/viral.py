"""
NeuroCron ViralEngine API
Referral programs, contests, gamification, and viral marketing
"""

import secrets
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User
from app.models.customer import CustomerProfile
from app.models.referral import (
    ReferralProgram, ReferralProgramStatus, Referral,
    Contest, ContestEntry, GamificationBadge, CustomerBadge, Leaderboard
)

router = APIRouter()


# === Schemas ===

class ReferralProgramCreate(BaseModel):
    name: str
    description: Optional[str] = None
    referrer_reward_type: str = "credit"
    referrer_reward_value: float = 10.0
    referred_reward_type: str = "discount"
    referred_reward_value: float = 10.0
    reward_on_event: str = "signup"


class ContestCreate(BaseModel):
    name: str
    description: Optional[str] = None
    prize_name: str
    prize_value: float = 0.0
    winner_count: int = 1
    starts_at: datetime
    ends_at: datetime
    entry_methods: List[dict] = []


class ContestEntrySubmit(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    action_type: str = "signup"


# === Helpers ===

async def verify_org_access(org_id: UUID, user_id: UUID, db: AsyncSession) -> bool:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


def generate_referral_code() -> str:
    return secrets.token_urlsafe(8).upper()[:10]


# === Referral Program ===

@router.get("/referral/programs")
async def list_referral_programs(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List referral programs."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ReferralProgram)
        .where(ReferralProgram.organization_id == org_id)
        .order_by(ReferralProgram.created_at.desc())
    )
    programs = result.scalars().all()
    
    return {
        "programs": [
            {
                "id": str(p.id),
                "name": p.name,
                "status": p.status.value,
                "referrer_reward": f"${p.referrer_reward_value} {p.referrer_reward_type}",
                "referred_reward": f"${p.referred_reward_value} {p.referred_reward_type}",
                "total_referrals": p.total_referrals,
                "successful_referrals": p.successful_referrals,
                "total_rewards_given": p.total_rewards_given,
            }
            for p in programs
        ]
    }


@router.post("/referral/programs")
async def create_referral_program(
    program: ReferralProgramCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a referral program."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_program = ReferralProgram(
        organization_id=org_id,
        name=program.name,
        description=program.description,
        referrer_reward_type=program.referrer_reward_type,
        referrer_reward_value=program.referrer_reward_value,
        referred_reward_type=program.referred_reward_type,
        referred_reward_value=program.referred_reward_value,
        reward_on_event=program.reward_on_event,
    )
    db.add(new_program)
    await db.commit()
    await db.refresh(new_program)
    
    return {"id": str(new_program.id), "message": "Referral program created"}


@router.post("/referral/programs/{program_id}/activate")
async def activate_program(
    program_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate a referral program."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(ReferralProgram)
        .where(ReferralProgram.id == program_id)
        .where(ReferralProgram.organization_id == org_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    program.status = ReferralProgramStatus.ACTIVE
    await db.commit()
    
    return {"message": "Program activated"}


@router.post("/referral/generate")
async def generate_referral_link(
    customer_id: UUID,
    program_id: UUID,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a referral link for a customer."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify program exists and is active
    program_result = await db.execute(
        select(ReferralProgram)
        .where(ReferralProgram.id == program_id)
        .where(ReferralProgram.organization_id == org_id)
        .where(ReferralProgram.status == ReferralProgramStatus.ACTIVE)
    )
    program = program_result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(status_code=404, detail="Active program not found")
    
    # Check for existing referral
    existing = await db.execute(
        select(Referral)
        .where(Referral.program_id == program_id)
        .where(Referral.referrer_id == customer_id)
        .where(Referral.referred_id == None)
    )
    existing_referral = existing.scalar_one_or_none()
    
    if existing_referral:
        return {
            "referral_code": existing_referral.referral_code,
            "referral_link": existing_referral.referral_link,
        }
    
    # Generate new referral
    code = generate_referral_code()
    link = f"https://neurocron.com/ref/{code}"
    
    new_referral = Referral(
        program_id=program_id,
        referrer_id=customer_id,
        referral_code=code,
        referral_link=link,
    )
    db.add(new_referral)
    await db.commit()
    
    return {
        "referral_code": code,
        "referral_link": link,
    }


@router.get("/referral/stats")
async def get_referral_stats(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get referral program statistics."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get all referrals for org
    result = await db.execute(
        select(Referral)
        .join(ReferralProgram, Referral.program_id == ReferralProgram.id)
        .where(ReferralProgram.organization_id == org_id)
    )
    referrals = result.scalars().all()
    
    total = len(referrals)
    converted = sum(1 for r in referrals if r.status == "converted" or r.status == "rewarded")
    total_clicks = sum(r.click_count for r in referrals)
    total_rewards = sum(r.referrer_reward_amount + r.referred_reward_amount for r in referrals if r.referrer_rewarded)
    
    return {
        "total_referrals": total,
        "successful_conversions": converted,
        "conversion_rate": round((converted / total * 100) if total > 0 else 0, 1),
        "total_clicks": total_clicks,
        "total_rewards_given": total_rewards,
        "viral_coefficient": round((converted / max(total, 1)) * 1.5, 2),
    }


# === Contests ===

@router.get("/contests")
async def list_contests(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List contests/giveaways."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Contest)
        .where(Contest.organization_id == org_id)
        .order_by(Contest.created_at.desc())
    )
    contests = result.scalars().all()
    
    return {
        "contests": [
            {
                "id": str(c.id),
                "name": c.name,
                "prize_name": c.prize_name,
                "prize_value": c.prize_value,
                "status": c.status,
                "total_entries": c.total_entries,
                "unique_participants": c.unique_participants,
                "starts_at": c.starts_at.isoformat(),
                "ends_at": c.ends_at.isoformat(),
            }
            for c in contests
        ]
    }


@router.post("/contests")
async def create_contest(
    contest: ContestCreate,
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a contest/giveaway."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_contest = Contest(
        organization_id=org_id,
        name=contest.name,
        description=contest.description,
        prize_name=contest.prize_name,
        prize_value=contest.prize_value,
        winner_count=contest.winner_count,
        starts_at=contest.starts_at,
        ends_at=contest.ends_at,
        entry_methods=contest.entry_methods,
    )
    db.add(new_contest)
    await db.commit()
    await db.refresh(new_contest)
    
    return {"id": str(new_contest.id), "message": "Contest created"}


@router.post("/contests/{contest_id}/enter")
async def enter_contest(
    contest_id: UUID,
    entry: ContestEntrySubmit,
    db: AsyncSession = Depends(get_db),
):
    """Submit a contest entry (public endpoint)."""
    # Get contest
    result = await db.execute(
        select(Contest)
        .where(Contest.id == contest_id)
        .where(Contest.status == "active")
    )
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found or not active")
    
    if datetime.utcnow() > contest.ends_at:
        raise HTTPException(status_code=400, detail="Contest has ended")
    
    # Check for existing entry
    existing = await db.execute(
        select(ContestEntry)
        .where(ContestEntry.contest_id == contest_id)
        .where(ContestEntry.email == entry.email)
    )
    existing_entry = existing.scalar_one_or_none()
    
    # Get points for action
    action_points = 10
    for method in contest.entry_methods:
        if method.get("type") == entry.action_type:
            action_points = method.get("points", 10)
            break
    
    if existing_entry:
        # Add more points for additional actions
        if entry.action_type not in [a.get("type") for a in existing_entry.actions_completed]:
            existing_entry.total_points += action_points
            existing_entry.actions_completed = existing_entry.actions_completed + [
                {"type": entry.action_type, "at": datetime.utcnow().isoformat()}
            ]
            await db.commit()
        return {
            "message": "Entry updated",
            "total_points": existing_entry.total_points,
        }
    
    # Create new entry
    new_entry = ContestEntry(
        contest_id=contest_id,
        email=entry.email,
        name=entry.name,
        total_points=action_points,
        actions_completed=[{"type": entry.action_type, "at": datetime.utcnow().isoformat()}],
    )
    db.add(new_entry)
    
    # Update contest stats
    contest.total_entries += 1
    contest.unique_participants += 1
    
    await db.commit()
    
    return {
        "message": "Entry submitted",
        "total_points": action_points,
    }


# === Gamification ===

@router.get("/badges")
async def list_badges(
    org_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List gamification badges."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(GamificationBadge)
        .where(GamificationBadge.organization_id == org_id)
        .where(GamificationBadge.is_active == True)
    )
    badges = result.scalars().all()
    
    return {
        "badges": [
            {
                "id": str(b.id),
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "criteria_type": b.criteria_type,
                "criteria_value": b.criteria_value,
                "points_reward": b.points_reward,
                "is_secret": b.is_secret,
            }
            for b in badges
        ]
    }


@router.get("/leaderboard")
async def get_leaderboard(
    org_id: UUID = Query(...),
    metric: str = Query("referrals", enum=["referrals", "points", "purchases"]),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard."""
    if not await verify_org_access(org_id, current_user.id, db):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if metric == "referrals":
        # Get top referrers
        result = await db.execute(
            select(
                CustomerProfile.id,
                CustomerProfile.email,
                CustomerProfile.first_name,
                CustomerProfile.last_name,
                func.count(Referral.id).label("count"),
            )
            .join(Referral, Referral.referrer_id == CustomerProfile.id)
            .where(CustomerProfile.organization_id == org_id)
            .where(Referral.status.in_(["converted", "rewarded"]))
            .group_by(CustomerProfile.id)
            .order_by(func.count(Referral.id).desc())
            .limit(limit)
        )
        rows = result.all()
        
        return {
            "leaderboard": [
                {
                    "rank": i + 1,
                    "customer_id": str(row.id),
                    "name": f"{row.first_name or ''} {row.last_name or ''}".strip() or row.email,
                    "value": row.count,
                    "metric": "referrals",
                }
                for i, row in enumerate(rows)
            ]
        }
    
    # Default: engagement-based leaderboard
    result = await db.execute(
        select(CustomerProfile)
        .where(CustomerProfile.organization_id == org_id)
        .order_by(CustomerProfile.engagement_score.desc())
        .limit(limit)
    )
    customers = result.scalars().all()
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "customer_id": str(c.id),
                "name": f"{c.first_name or ''} {c.last_name or ''}".strip() or c.email,
                "value": c.engagement_score,
                "metric": "engagement",
            }
            for i, c in enumerate(customers)
        ]
    }

