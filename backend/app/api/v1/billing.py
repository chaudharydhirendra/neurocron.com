"""
NeuroCron Billing API
Stripe subscription and payment management
"""

import os
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import stripe

from app.core.deps import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.organization import Organization, OrganizationMember
from app.models.user import User

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")

# Pricing plans
PLANS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "stripe_price_monthly": None,
        "stripe_price_yearly": None,
        "limits": {
            "campaigns": 3,
            "team_members": 1,
            "ai_tokens": 10000,
            "integrations": 2,
            "flows": 3,
            "personas": 5,
        },
        "features": [
            "3 Active Campaigns",
            "Basic Analytics",
            "1 Team Member",
            "10K AI Tokens/month",
            "Email Support",
        ],
    },
    "starter": {
        "name": "Starter",
        "price_monthly": 49,
        "price_yearly": 470,  # ~20% discount
        "stripe_price_monthly": os.getenv("STRIPE_STARTER_MONTHLY"),
        "stripe_price_yearly": os.getenv("STRIPE_STARTER_YEARLY"),
        "limits": {
            "campaigns": 10,
            "team_members": 3,
            "ai_tokens": 50000,
            "integrations": 5,
            "flows": 10,
            "personas": 20,
        },
        "features": [
            "10 Active Campaigns",
            "Advanced Analytics",
            "3 Team Members",
            "50K AI Tokens/month",
            "NeuroCopilot Access",
            "FlowBuilder",
            "Priority Support",
        ],
    },
    "growth": {
        "name": "Growth",
        "price_monthly": 149,
        "price_yearly": 1430,
        "stripe_price_monthly": os.getenv("STRIPE_GROWTH_MONTHLY"),
        "stripe_price_yearly": os.getenv("STRIPE_GROWTH_YEARLY"),
        "limits": {
            "campaigns": 50,
            "team_members": 10,
            "ai_tokens": 200000,
            "integrations": 15,
            "flows": 50,
            "personas": 100,
        },
        "features": [
            "50 Active Campaigns",
            "All Analytics Features",
            "10 Team Members",
            "200K AI Tokens/month",
            "All Integrations",
            "Unlimited Flows",
            "BattleStation Access",
            "Dedicated Support",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": None,  # Custom pricing
        "price_yearly": None,
        "stripe_price_monthly": None,
        "stripe_price_yearly": None,
        "limits": {
            "campaigns": -1,  # Unlimited
            "team_members": -1,
            "ai_tokens": -1,
            "integrations": -1,
            "flows": -1,
            "personas": -1,
        },
        "features": [
            "Unlimited Everything",
            "Custom Integrations",
            "SLA Guarantee",
            "Dedicated Account Manager",
            "Custom Training",
            "On-premise Option",
            "Priority Feature Requests",
        ],
    },
}


class SubscriptionCreate(BaseModel):
    """Create subscription request"""
    plan: str  # starter, growth
    interval: str = "month"  # month, year


class SubscriptionUpdate(BaseModel):
    """Update subscription request"""
    plan: str


@router.get("/plans")
async def get_plans(
    current_user: User = Depends(get_current_user)
):
    """Get available subscription plans."""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan["name"],
                "price_monthly": plan["price_monthly"],
                "price_yearly": plan["price_yearly"],
                "features": plan["features"],
                "limits": plan["limits"],
                "is_custom": plan["price_monthly"] is None,
            }
            for plan_id, plan in PLANS.items()
        ]
    }


@router.get("/subscription")
async def get_subscription(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current subscription for an organization."""
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
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Return current plan info
    current_plan = org.plan.value if hasattr(org.plan, 'value') else str(org.plan).lower()
    plan_info = PLANS.get(current_plan, PLANS["free"])
    
    return {
        "plan": current_plan,
        "plan_name": plan_info["name"],
        "status": "active",
        "limits": plan_info["limits"],
        "features": plan_info["features"],
        "current_period_end": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "cancel_at_period_end": False,
    }


@router.post("/checkout")
async def create_checkout_session(
    subscription: SubscriptionCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription."""
    # Verify membership (must be owner/admin)
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to manage billing"
        )
    
    # Validate plan
    if subscription.plan not in PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    plan = PLANS[subscription.plan]
    if subscription.interval == "year":
        price_id = plan.get("stripe_price_yearly")
    else:
        price_id = plan.get("stripe_price_monthly")
    
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan not available for subscription"
        )
    
    # In production, create actual Stripe checkout session
    # For now, return mock session
    return {
        "checkout_url": f"https://checkout.stripe.com/c/pay/demo_{subscription.plan}_{subscription.interval}",
        "session_id": f"cs_demo_{org_id}_{subscription.plan}",
        "message": "Redirect user to checkout_url to complete payment",
    }


@router.post("/portal")
async def create_billing_portal(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create Stripe billing portal session."""
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to access billing"
        )
    
    # In production, create actual portal session
    return {
        "portal_url": "https://billing.stripe.com/p/demo_portal",
        "message": "Redirect user to portal_url to manage billing",
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For development without signature verification
            import json
            event = json.loads(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Handle events
    event_type = event.get("type", "")
    
    if event_type == "checkout.session.completed":
        # Activate subscription
        pass
    elif event_type == "customer.subscription.updated":
        # Update subscription status
        pass
    elif event_type == "customer.subscription.deleted":
        # Handle cancellation
        pass
    elif event_type == "invoice.paid":
        # Record payment
        pass
    elif event_type == "invoice.payment_failed":
        # Handle failed payment
        pass
    
    return {"received": True}


@router.get("/usage")
async def get_usage(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current usage metrics for an organization."""
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
    
    # Get organization
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    current_plan = org.plan.value if hasattr(org.plan, 'value') else str(org.plan).lower() if org else "free"
    plan_limits = PLANS.get(current_plan, PLANS["free"])["limits"]
    
    # In production, calculate actual usage
    return {
        "usage": {
            "campaigns": {"used": 2, "limit": plan_limits["campaigns"]},
            "team_members": {"used": 1, "limit": plan_limits["team_members"]},
            "ai_tokens": {"used": 4500, "limit": plan_limits["ai_tokens"]},
            "integrations": {"used": 1, "limit": plan_limits["integrations"]},
            "flows": {"used": 1, "limit": plan_limits["flows"]},
            "personas": {"used": 3, "limit": plan_limits["personas"]},
        },
        "period_start": (datetime.utcnow().replace(day=1)).isoformat(),
        "period_end": (datetime.utcnow().replace(day=1) + timedelta(days=30)).isoformat(),
    }


@router.get("/invoices")
async def get_invoices(
    org_id: UUID = Query(..., description="Organization ID"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get billing invoices for an organization."""
    # Verify membership
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.user_id == current_user.id)
        .where(OrganizationMember.role.in_(["owner", "admin"]))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be owner or admin to view invoices"
        )
    
    # In production, fetch from database
    return {
        "invoices": [
            {
                "id": "inv_demo_1",
                "amount": 4900,  # $49.00
                "currency": "usd",
                "status": "paid",
                "date": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "invoice_url": "#",
            },
        ]
    }

