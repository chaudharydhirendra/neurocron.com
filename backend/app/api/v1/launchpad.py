"""
NeuroCron LaunchPad API
Pre-built campaign templates for quick launch
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter()


# Campaign Templates
CAMPAIGN_TEMPLATES = {
    "product_launch": {
        "id": "product_launch",
        "name": "Product Launch",
        "category": "launch",
        "description": "Complete product launch campaign with multi-channel strategy",
        "duration_days": 30,
        "estimated_budget": {"min": 5000, "max": 20000},
        "channels": ["google_ads", "meta_ads", "email", "social"],
        "components": {
            "pre_launch": {
                "name": "Pre-Launch Phase (Week 1)",
                "tasks": [
                    "Create landing page",
                    "Set up email capture",
                    "Develop teaser content",
                    "Build anticipation on social",
                ]
            },
            "launch": {
                "name": "Launch Phase (Week 2)",
                "tasks": [
                    "Launch paid ads",
                    "Send announcement emails",
                    "Publish blog post",
                    "Social media blitz",
                    "Press release distribution",
                ]
            },
            "post_launch": {
                "name": "Post-Launch (Week 3-4)",
                "tasks": [
                    "Collect testimonials",
                    "Retargeting campaigns",
                    "Performance optimization",
                    "User feedback collection",
                ]
            }
        },
        "content_templates": [
            {"type": "email", "name": "Launch Announcement"},
            {"type": "social", "name": "Launch Posts (5x)"},
            {"type": "ad", "name": "Product Ads (3 variants)"},
            {"type": "landing", "name": "Product Landing Page"},
        ],
        "kpis": ["sign_ups", "sales", "website_traffic", "social_engagement"],
    },
    "black_friday": {
        "id": "black_friday",
        "name": "Black Friday / Holiday Sale",
        "category": "seasonal",
        "description": "High-impact holiday sales campaign",
        "duration_days": 14,
        "estimated_budget": {"min": 10000, "max": 50000},
        "channels": ["google_ads", "meta_ads", "email", "sms"],
        "components": {
            "early_access": {
                "name": "Early Access (3 days before)",
                "tasks": [
                    "VIP early access emails",
                    "Teaser ads",
                    "Countdown timer on site",
                ]
            },
            "main_sale": {
                "name": "Main Sale Period",
                "tasks": [
                    "Launch all ad campaigns",
                    "Email blast to full list",
                    "Social media posts every 4 hours",
                    "SMS reminders",
                ]
            },
            "last_chance": {
                "name": "Last Chance (Final 24 hours)",
                "tasks": [
                    "Urgency messaging",
                    "Cart abandonment push",
                    "Final reminder emails",
                ]
            }
        },
        "content_templates": [
            {"type": "email", "name": "Early Access Email"},
            {"type": "email", "name": "Main Sale Announcement"},
            {"type": "email", "name": "Last Chance Reminder"},
            {"type": "ad", "name": "Black Friday Ads (5 variants)"},
            {"type": "sms", "name": "SMS Templates (3x)"},
        ],
        "kpis": ["revenue", "conversion_rate", "roas", "average_order_value"],
    },
    "webinar_promo": {
        "id": "webinar_promo",
        "name": "Webinar Promotion",
        "category": "lead_gen",
        "description": "Fill your webinar with qualified registrants",
        "duration_days": 21,
        "estimated_budget": {"min": 2000, "max": 10000},
        "channels": ["email", "linkedin", "meta_ads", "social"],
        "components": {
            "announcement": {
                "name": "Announcement Phase (Week 1)",
                "tasks": [
                    "Create registration landing page",
                    "Email announcement to list",
                    "LinkedIn posts and articles",
                    "Paid ads launch",
                ]
            },
            "reminder": {
                "name": "Reminder Phase (Week 2)",
                "tasks": [
                    "Reminder emails to registered",
                    "Social proof posts",
                    "Partner/affiliate promotion",
                    "Retargeting non-registered",
                ]
            },
            "final_push": {
                "name": "Final Push (Week 3)",
                "tasks": [
                    "Last chance emails",
                    "24-hour countdown",
                    "Live event prep",
                    "Post-webinar follow-up setup",
                ]
            }
        },
        "content_templates": [
            {"type": "landing", "name": "Webinar Registration Page"},
            {"type": "email", "name": "Invitation Email Sequence (4x)"},
            {"type": "social", "name": "LinkedIn Posts (6x)"},
            {"type": "ad", "name": "Registration Ads (3 variants)"},
        ],
        "kpis": ["registrations", "attendance_rate", "engagement", "leads_generated"],
    },
    "brand_awareness": {
        "id": "brand_awareness",
        "name": "Brand Awareness Campaign",
        "category": "branding",
        "description": "Increase brand visibility and recognition",
        "duration_days": 60,
        "estimated_budget": {"min": 5000, "max": 30000},
        "channels": ["youtube", "instagram", "tiktok", "display"],
        "components": {
            "content_creation": {
                "name": "Content Creation",
                "tasks": [
                    "Develop brand story video",
                    "Create social content series",
                    "Design display ads",
                    "Influencer partnership outreach",
                ]
            },
            "distribution": {
                "name": "Distribution Phase",
                "tasks": [
                    "Launch video ads",
                    "Social media posting schedule",
                    "Influencer collaborations",
                    "PR activities",
                ]
            },
            "amplification": {
                "name": "Amplification",
                "tasks": [
                    "Boost top-performing content",
                    "Expand audience targeting",
                    "Community engagement",
                    "User-generated content campaign",
                ]
            }
        },
        "content_templates": [
            {"type": "video", "name": "Brand Story Video"},
            {"type": "social", "name": "Social Content Calendar (30 days)"},
            {"type": "ad", "name": "Display Ads (5 sizes)"},
            {"type": "influencer", "name": "Influencer Brief"},
        ],
        "kpis": ["reach", "impressions", "brand_recall", "social_followers"],
    },
    "lead_generation": {
        "id": "lead_generation",
        "name": "Lead Generation Machine",
        "category": "lead_gen",
        "description": "Systematic B2B lead generation campaign",
        "duration_days": 30,
        "estimated_budget": {"min": 3000, "max": 15000},
        "channels": ["linkedin", "google_ads", "email", "content"],
        "components": {
            "lead_magnet": {
                "name": "Lead Magnet Creation",
                "tasks": [
                    "Create downloadable asset",
                    "Build landing page",
                    "Set up email automation",
                    "CRM integration",
                ]
            },
            "traffic_generation": {
                "name": "Traffic Generation",
                "tasks": [
                    "Launch LinkedIn ads",
                    "Google Search ads",
                    "Content marketing",
                    "Social promotion",
                ]
            },
            "nurturing": {
                "name": "Lead Nurturing",
                "tasks": [
                    "Email drip campaign",
                    "Retargeting ads",
                    "Sales team handoff",
                    "Qualification scoring",
                ]
            }
        },
        "content_templates": [
            {"type": "ebook", "name": "Lead Magnet (eBook/Guide)"},
            {"type": "landing", "name": "Lead Capture Page"},
            {"type": "email", "name": "Nurture Sequence (5 emails)"},
            {"type": "ad", "name": "LinkedIn Ads (4 variants)"},
        ],
        "kpis": ["leads_generated", "cost_per_lead", "lead_quality_score", "conversion_to_opportunity"],
    },
    "app_launch": {
        "id": "app_launch",
        "name": "Mobile App Launch",
        "category": "launch",
        "description": "Launch your mobile app with maximum downloads",
        "duration_days": 45,
        "estimated_budget": {"min": 8000, "max": 40000},
        "channels": ["app_store_ads", "meta_ads", "google_uac", "influencer"],
        "components": {
            "pre_launch": {
                "name": "Pre-Launch",
                "tasks": [
                    "App store optimization",
                    "Beta testing campaign",
                    "Build waitlist",
                    "Press kit preparation",
                ]
            },
            "launch": {
                "name": "Launch Week",
                "tasks": [
                    "App store feature pitch",
                    "UA campaign launch",
                    "Influencer promotions",
                    "Press outreach",
                ]
            },
            "growth": {
                "name": "Growth Phase",
                "tasks": [
                    "Optimize campaigns",
                    "Referral program launch",
                    "Review generation",
                    "Retention campaigns",
                ]
            }
        },
        "content_templates": [
            {"type": "video", "name": "App Preview Video"},
            {"type": "graphics", "name": "App Store Assets"},
            {"type": "ad", "name": "UA Ads (6 variants)"},
            {"type": "email", "name": "Launch Email Sequence"},
        ],
        "kpis": ["downloads", "cost_per_install", "day_1_retention", "app_store_rating"],
    },
}


class TemplateCategory(BaseModel):
    id: str
    name: str
    count: int


class TemplateListItem(BaseModel):
    id: str
    name: str
    category: str
    description: str
    duration_days: int
    estimated_budget: dict
    channels: List[str]


class TemplateDetail(BaseModel):
    id: str
    name: str
    category: str
    description: str
    duration_days: int
    estimated_budget: dict
    channels: List[str]
    components: dict
    content_templates: List[dict]
    kpis: List[str]


@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_user)
):
    """Get template categories."""
    categories = {}
    for template in CAMPAIGN_TEMPLATES.values():
        cat = template["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    category_names = {
        "launch": "Product Launch",
        "seasonal": "Seasonal & Holidays",
        "lead_gen": "Lead Generation",
        "branding": "Brand Awareness",
    }
    
    return {
        "categories": [
            {"id": k, "name": category_names.get(k, k.title()), "count": v}
            for k, v in categories.items()
        ]
    }


@router.get("/", response_model=List[TemplateListItem])
async def list_templates(
    category: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """List all available campaign templates."""
    templates = []
    for template in CAMPAIGN_TEMPLATES.values():
        if category and template["category"] != category:
            continue
        templates.append(TemplateListItem(
            id=template["id"],
            name=template["name"],
            category=template["category"],
            description=template["description"],
            duration_days=template["duration_days"],
            estimated_budget=template["estimated_budget"],
            channels=template["channels"],
        ))
    return templates


@router.get("/{template_id}", response_model=TemplateDetail)
async def get_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get template details."""
    if template_id not in CAMPAIGN_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template = CAMPAIGN_TEMPLATES[template_id]
    return TemplateDetail(**template)


@router.post("/{template_id}/launch")
async def launch_from_template(
    template_id: str,
    org_id: UUID = Query(...),
    customization: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Launch a campaign from a template."""
    if template_id not in CAMPAIGN_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    template = CAMPAIGN_TEMPLATES[template_id]
    
    # In production:
    # 1. Create campaign from template
    # 2. Generate all content using AI
    # 3. Set up automation flows
    # 4. Create tasks in ProjectHub
    
    return {
        "success": True,
        "message": f"Campaign created from {template['name']} template",
        "campaign_id": "new-campaign-id",
        "tasks_created": sum(len(phase["tasks"]) for phase in template["components"].values()),
        "next_steps": [
            "Review and customize generated content",
            "Set campaign budget",
            "Configure target audience",
            "Schedule launch date",
        ]
    }

