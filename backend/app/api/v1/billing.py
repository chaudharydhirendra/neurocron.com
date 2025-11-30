"""
NeuroCron Billing API
Stripe subscription and payment management with real checkout flow
"""

import os
from typing import Optional, List
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import stripe

from app.core.deps import get_db
from app.core.config import settings
from app.api.v1.auth import get_current_user
from app.models.organization import Organization, OrganizationMember, PlanType
from app.models.user import User
from app.models.billing import Subscription, Invoice, UsageRecord

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Pricing plans with Stripe Price IDs
PLANS = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "price_yearly": 0,
        "stripe_price_monthly": None,
        "stripe_price_yearly": None,
        "plan_type": PlanType.FREE,
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
        "price_yearly": 470,
        "stripe_price_monthly": os.getenv("STRIPE_STARTER_MONTHLY", "price_starter_monthly"),
        "stripe_price_yearly": os.getenv("STRIPE_STARTER_YEARLY", "price_starter_yearly"),
        "plan_type": PlanType.STARTER,
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
        "stripe_price_monthly": os.getenv("STRIPE_GROWTH_MONTHLY", "price_growth_monthly"),
        "stripe_price_yearly": os.getenv("STRIPE_GROWTH_YEARLY", "price_growth_yearly"),
        "plan_type": PlanType.GROWTH,
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
        "price_monthly": None,
        "price_yearly": None,
        "stripe_price_monthly": None,
        "stripe_price_yearly": None,
        "plan_type": PlanType.ENTERPRISE,
        "limits": {
            "campaigns": -1,
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
    interval: str = "month"


@router.get("/plans")
async def get_plans(
    current_user: User = Depends(get_current_user)
):
    """Get available subscription plans with pricing."""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan["name"],
                "price_monthly": plan["price_monthly"],
                "price_yearly": plan["price_yearly"],
                "features": plan["features"],
                "limits": plan["limits"],
                "popular": plan_id == "growth",
            }
            for plan_id, plan in PLANS.items()
        ],
        "stripe_configured": bool(stripe.api_key and stripe.api_key != ""),
    }


@router.get("/subscription")
async def get_subscription(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current subscription status for an organization."""
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
    
    # Get subscription from database
    result = await db.execute(
        select(Subscription)
        .where(Subscription.organization_id == org_id)
        .where(Subscription.status.in_(["active", "trialing"]))
    )
    subscription = result.scalar_one_or_none()
    
    current_plan = org.plan.value if org.plan else "free"
    plan_details = PLANS.get(current_plan, PLANS["free"])
    
    if subscription:
        return {
            "active": True,
            "plan": current_plan,
            "plan_name": plan_details["name"],
            "status": subscription.status,
            "current_period_end": subscription.current_period_end.isoformat() if subscription.current_period_end else None,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "limits": plan_details["limits"],
            "features": plan_details["features"],
            "stripe_subscription_id": subscription.stripe_subscription_id,
        }
    else:
        return {
            "active": True,
            "plan": "free",
            "plan_name": "Free",
            "status": "active",
            "limits": PLANS["free"]["limits"],
            "features": PLANS["free"]["features"],
        }


@router.post("/checkout")
async def create_checkout_session(
    request: SubscriptionCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe Checkout session for subscription."""
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY environment variable."
        )
    
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
    
    # Validate plan
    if request.plan not in PLANS or request.plan in ["free", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {request.plan}. Use 'starter' or 'growth'."
        )
    
    plan = PLANS[request.plan]
    price_id = plan["stripe_price_yearly"] if request.interval == "year" else plan["stripe_price_monthly"]
    
    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe price not configured for {request.plan} {request.interval}ly plan."
        )
    
    # Get or create Stripe customer
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    
    stripe_customer_id = org.settings.get("stripe_customer_id") if org.settings else None
    
    if not stripe_customer_id:
        try:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=org.name,
                metadata={
                    "organization_id": str(org_id),
                    "user_id": str(current_user.id),
                },
            )
            stripe_customer_id = customer.id
            
            # Save customer ID
            if not org.settings:
                org.settings = {}
            org.settings["stripe_customer_id"] = stripe_customer_id
            await db.commit()
        except stripe.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize billing"
            )
    
    # Create checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            mode="subscription",
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            success_url=f"{settings.FRONTEND_URL}/billing?success=true&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/billing?canceled=true",
            metadata={
                "organization_id": str(org_id),
                "plan": request.plan,
                "interval": request.interval,
            },
            subscription_data={
                "metadata": {
                    "organization_id": str(org_id),
                    "plan": request.plan,
                },
            },
            allow_promotion_codes=True,
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        }
    except stripe.StripeError as e:
        logger.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )


@router.post("/portal")
async def create_billing_portal(
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe Billing Portal session for managing subscription."""
    if not stripe.api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stripe is not configured"
        )
    
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
    
    stripe_customer_id = org.settings.get("stripe_customer_id") if org.settings else None
    
    if not stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found. Start a subscription first."
        )
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=f"{settings.FRONTEND_URL}/billing",
        )
        
        return {
            "portal_url": portal_session.url,
        }
    except stripe.StripeError as e:
        logger.error(f"Failed to create billing portal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to access billing portal"
        )


@router.get("/invoices")
async def get_invoices(
    org_id: UUID = Query(..., description="Organization ID"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoice history for an organization."""
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
    
    # Get from database first
    result = await db.execute(
        select(Invoice)
        .where(Invoice.organization_id == org_id)
        .order_by(Invoice.created_at.desc())
        .limit(limit)
    )
    db_invoices = result.scalars().all()
    
    invoices = [
        {
            "id": str(inv.id),
            "stripe_invoice_id": inv.stripe_invoice_id,
            "amount": inv.amount_due / 100,  # Convert from cents
            "currency": inv.currency,
            "status": inv.status,
            "created_at": inv.created_at.isoformat(),
            "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
            "invoice_pdf": inv.invoice_pdf_url,
        }
        for inv in db_invoices
    ]
    
    # If Stripe is configured, also try to fetch latest from Stripe
    if stripe.api_key:
        result = await db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        org = result.scalar_one_or_none()
        stripe_customer_id = org.settings.get("stripe_customer_id") if org and org.settings else None
        
        if stripe_customer_id:
            try:
                stripe_invoices = stripe.Invoice.list(
                    customer=stripe_customer_id,
                    limit=limit,
                )
                
                # Merge with database invoices (use Stripe as source of truth)
                stripe_invoice_ids = {inv.stripe_invoice_id for inv in db_invoices}
                
                for sinv in stripe_invoices.data:
                    if sinv.id not in stripe_invoice_ids:
                        invoices.append({
                            "id": sinv.id,
                            "stripe_invoice_id": sinv.id,
                            "amount": sinv.amount_due / 100,
                            "currency": sinv.currency,
                            "status": sinv.status,
                            "created_at": datetime.fromtimestamp(sinv.created).isoformat(),
                            "paid_at": datetime.fromtimestamp(sinv.status_transitions.paid_at).isoformat() if sinv.status_transitions.paid_at else None,
                            "invoice_pdf": sinv.invoice_pdf,
                        })
                
                # Sort by date
                invoices.sort(key=lambda x: x["created_at"], reverse=True)
            except stripe.StripeError as e:
                logger.warning(f"Failed to fetch Stripe invoices: {e}")
    
    return {"invoices": invoices[:limit]}


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
    
    current_plan = org.plan.value if org and org.plan else "free"
    limits = PLANS.get(current_plan, PLANS["free"])["limits"]
    
    # Get current month's usage
    from sqlalchemy import func
    result = await db.execute(
        select(
            UsageRecord.metric_type,
            func.sum(UsageRecord.quantity).label("total")
        )
        .where(UsageRecord.organization_id == org_id)
        .where(UsageRecord.period_start >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0))
        .group_by(UsageRecord.metric_type)
    )
    usage_data = {row.metric_type: int(row.total) for row in result.all()}
    
    # Count campaigns
    from app.models.campaign import Campaign
    result = await db.execute(
        select(func.count(Campaign.id))
        .where(Campaign.organization_id == org_id)
        .where(Campaign.status == "active")
    )
    active_campaigns = result.scalar() or 0
    
    # Count team members
    result = await db.execute(
        select(func.count(OrganizationMember.id))
        .where(OrganizationMember.organization_id == org_id)
        .where(OrganizationMember.is_active == True)
    )
    team_members = result.scalar() or 0
    
    return {
        "usage": {
            "campaigns": {
                "used": active_campaigns,
                "limit": limits["campaigns"],
                "percentage": round((active_campaigns / limits["campaigns"]) * 100) if limits["campaigns"] > 0 else 100,
            },
            "team_members": {
                "used": team_members,
                "limit": limits["team_members"],
                "percentage": round((team_members / limits["team_members"]) * 100) if limits["team_members"] > 0 else 100,
            },
            "ai_tokens": {
                "used": usage_data.get("ai_tokens", 0),
                "limit": limits["ai_tokens"],
                "percentage": round((usage_data.get("ai_tokens", 0) / limits["ai_tokens"]) * 100) if limits["ai_tokens"] > 0 else 100,
            },
        },
        "plan": current_plan,
        "period": datetime.utcnow().strftime("%B %Y"),
    }


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhooks for subscription events."""
    if not STRIPE_WEBHOOK_SECRET:
        logger.warning("Stripe webhook secret not configured")
        return {"received": True}
    
    payload = await request.body()
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    event_type = event["type"]
    data = event["data"]["object"]
    
    logger.info(f"Received Stripe webhook: {event_type}")
    
    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(db, data)
        
        elif event_type == "customer.subscription.created":
            await _handle_subscription_created(db, data)
        
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(db, data)
        
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(db, data)
        
        elif event_type == "invoice.paid":
            await _handle_invoice_paid(db, data)
        
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(db, data)
        
        await db.commit()
    except Exception as e:
        logger.error(f"Error handling webhook {event_type}: {e}")
        await db.rollback()
    
    return {"received": True}


async def _handle_checkout_completed(db: AsyncSession, session: dict):
    """Handle successful checkout completion."""
    org_id = session.get("metadata", {}).get("organization_id")
    plan = session.get("metadata", {}).get("plan")
    
    if not org_id or not plan:
        logger.warning("Missing metadata in checkout session")
        return
    
    logger.info(f"Checkout completed for org {org_id}, plan: {plan}")


async def _handle_subscription_created(db: AsyncSession, subscription: dict):
    """Handle new subscription creation."""
    metadata = subscription.get("metadata", {})
    org_id = metadata.get("organization_id")
    plan = metadata.get("plan")
    
    if not org_id:
        logger.warning("Missing organization_id in subscription metadata")
        return
    
    # Create/update subscription record
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription["id"])
    )
    sub = result.scalar_one_or_none()
    
    if not sub:
        sub = Subscription(
            organization_id=UUID(org_id),
            stripe_subscription_id=subscription["id"],
            stripe_customer_id=subscription["customer"],
        )
        db.add(sub)
    
    sub.status = subscription["status"]
    sub.plan = plan or "starter"
    sub.current_period_start = datetime.fromtimestamp(subscription["current_period_start"])
    sub.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    sub.cancel_at_period_end = subscription.get("cancel_at_period_end", False)
    
    # Update organization plan
    result = await db.execute(
        select(Organization).where(Organization.id == UUID(org_id))
    )
    org = result.scalar_one_or_none()
    if org and plan:
        org.plan = PLANS.get(plan, {}).get("plan_type", PlanType.STARTER)
    
    logger.info(f"Subscription created: {subscription['id']} for org {org_id}")


async def _handle_subscription_updated(db: AsyncSession, subscription: dict):
    """Handle subscription updates (plan changes, cancellations)."""
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription["id"])
    )
    sub = result.scalar_one_or_none()
    
    if not sub:
        logger.warning(f"Subscription not found: {subscription['id']}")
        return
    
    sub.status = subscription["status"]
    sub.current_period_end = datetime.fromtimestamp(subscription["current_period_end"])
    sub.cancel_at_period_end = subscription.get("cancel_at_period_end", False)
    
    logger.info(f"Subscription updated: {subscription['id']}")


async def _handle_subscription_deleted(db: AsyncSession, subscription: dict):
    """Handle subscription cancellation."""
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription["id"])
    )
    sub = result.scalar_one_or_none()
    
    if sub:
        sub.status = "canceled"
        sub.ended_at = datetime.utcnow()
        
        # Downgrade organization to free
        result = await db.execute(
            select(Organization).where(Organization.id == sub.organization_id)
        )
        org = result.scalar_one_or_none()
        if org:
            org.plan = PlanType.FREE
        
        logger.info(f"Subscription deleted: {subscription['id']}")


async def _handle_invoice_paid(db: AsyncSession, invoice: dict):
    """Handle successful payment."""
    # Store invoice
    result = await db.execute(
        select(Invoice).where(Invoice.stripe_invoice_id == invoice["id"])
    )
    inv = result.scalar_one_or_none()
    
    if not inv:
        # Find organization
        customer_id = invoice["customer"]
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        sub = result.scalar_one_or_none()
        
        if sub:
            inv = Invoice(
                organization_id=sub.organization_id,
                stripe_invoice_id=invoice["id"],
                stripe_customer_id=customer_id,
                amount_due=invoice["amount_due"],
                amount_paid=invoice["amount_paid"],
                currency=invoice["currency"],
                status="paid",
                paid_at=datetime.utcnow(),
                invoice_pdf_url=invoice.get("invoice_pdf"),
            )
            db.add(inv)
    else:
        inv.status = "paid"
        inv.amount_paid = invoice["amount_paid"]
        inv.paid_at = datetime.utcnow()
    
    logger.info(f"Invoice paid: {invoice['id']}")


async def _handle_payment_failed(db: AsyncSession, invoice: dict):
    """Handle failed payment."""
    result = await db.execute(
        select(Invoice).where(Invoice.stripe_invoice_id == invoice["id"])
    )
    inv = result.scalar_one_or_none()
    
    if inv:
        inv.status = "failed"
    
    # TODO: Send notification to organization owner
    logger.warning(f"Payment failed for invoice: {invoice['id']}")


@router.post("/usage/record")
async def record_usage(
    metric_type: str,
    quantity: int,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record usage for billing/limits tracking (internal use)."""
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
    
    # Record usage
    usage = UsageRecord(
        organization_id=org_id,
        metric_type=metric_type,
        quantity=quantity,
        period_start=datetime.utcnow().replace(day=1, hour=0, minute=0, second=0),
        period_end=datetime.utcnow().replace(day=28, hour=23, minute=59, second=59),
    )
    db.add(usage)
    await db.commit()
    
    return {"recorded": True}
