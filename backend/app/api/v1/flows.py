"""
NeuroCron FlowBuilder API
Visual automation builder endpoints
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.organization import OrganizationMember
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class FlowNode(BaseModel):
    """Flow node schema"""
    id: str
    type: str  # trigger, action, condition, delay, split, end
    position: dict  # {x: number, y: number}
    data: dict  # Node-specific configuration


class FlowEdge(BaseModel):
    """Flow edge (connection) schema"""
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    label: Optional[str] = None


class FlowCreate(BaseModel):
    """Create flow request"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    nodes: List[FlowNode] = []
    edges: List[FlowEdge] = []


class FlowUpdate(BaseModel):
    """Update flow request"""
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[FlowNode]] = None
    edges: Optional[List[FlowEdge]] = None
    status: Optional[str] = None


class FlowResponse(BaseModel):
    """Flow response"""
    id: str
    name: str
    description: Optional[str]
    status: str
    nodes: List[dict]
    edges: List[dict]
    total_executions: int
    successful_executions: int
    created_at: str
    updated_at: str


# Flow templates
FLOW_TEMPLATES = {
    "welcome_series": {
        "name": "Welcome Email Series",
        "description": "Automated welcome emails for new subscribers",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 250, "y": 0}, 
             "data": {"label": "New Subscriber", "trigger_type": "form_submit"}},
            {"id": "action-1", "type": "action", "position": {"x": 250, "y": 100},
             "data": {"label": "Send Welcome Email", "action_type": "send_email", "template": "welcome"}},
            {"id": "delay-1", "type": "delay", "position": {"x": 250, "y": 200},
             "data": {"label": "Wait 2 Days", "delay_value": 2, "delay_unit": "days"}},
            {"id": "action-2", "type": "action", "position": {"x": 250, "y": 300},
             "data": {"label": "Send Tips Email", "action_type": "send_email", "template": "tips"}},
            {"id": "end-1", "type": "end", "position": {"x": 250, "y": 400},
             "data": {"label": "End"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "action-1"},
            {"id": "e2", "source": "action-1", "target": "delay-1"},
            {"id": "e3", "source": "delay-1", "target": "action-2"},
            {"id": "e4", "source": "action-2", "target": "end-1"},
        ],
    },
    "abandoned_cart": {
        "name": "Abandoned Cart Recovery",
        "description": "Recover abandoned shopping carts",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 250, "y": 0},
             "data": {"label": "Cart Abandoned", "trigger_type": "cart_abandoned"}},
            {"id": "delay-1", "type": "delay", "position": {"x": 250, "y": 100},
             "data": {"label": "Wait 1 Hour", "delay_value": 1, "delay_unit": "hours"}},
            {"id": "condition-1", "type": "condition", "position": {"x": 250, "y": 200},
             "data": {"label": "Cart Still Abandoned?", "condition_type": "cart_status"}},
            {"id": "action-1", "type": "action", "position": {"x": 100, "y": 300},
             "data": {"label": "Send Reminder Email", "action_type": "send_email"}},
            {"id": "end-1", "type": "end", "position": {"x": 400, "y": 300},
             "data": {"label": "Purchased"}},
            {"id": "delay-2", "type": "delay", "position": {"x": 100, "y": 400},
             "data": {"label": "Wait 24 Hours", "delay_value": 24, "delay_unit": "hours"}},
            {"id": "action-2", "type": "action", "position": {"x": 100, "y": 500},
             "data": {"label": "Send Discount Email", "action_type": "send_email", "discount": 10}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "delay-1"},
            {"id": "e2", "source": "delay-1", "target": "condition-1"},
            {"id": "e3", "source": "condition-1", "target": "action-1", "label": "Yes"},
            {"id": "e4", "source": "condition-1", "target": "end-1", "label": "No"},
            {"id": "e5", "source": "action-1", "target": "delay-2"},
            {"id": "e6", "source": "delay-2", "target": "action-2"},
        ],
    },
    "lead_nurturing": {
        "name": "Lead Nurturing Sequence",
        "description": "Nurture leads with educational content",
        "nodes": [
            {"id": "trigger-1", "type": "trigger", "position": {"x": 250, "y": 0},
             "data": {"label": "New Lead", "trigger_type": "lead_created"}},
            {"id": "action-1", "type": "action", "position": {"x": 250, "y": 100},
             "data": {"label": "Add to CRM", "action_type": "crm_add"}},
            {"id": "action-2", "type": "action", "position": {"x": 250, "y": 200},
             "data": {"label": "Send Intro Email", "action_type": "send_email"}},
            {"id": "delay-1", "type": "delay", "position": {"x": 250, "y": 300},
             "data": {"label": "Wait 3 Days", "delay_value": 3, "delay_unit": "days"}},
            {"id": "condition-1", "type": "condition", "position": {"x": 250, "y": 400},
             "data": {"label": "Opened Email?", "condition_type": "email_opened"}},
            {"id": "action-3", "type": "action", "position": {"x": 100, "y": 500},
             "data": {"label": "Send Case Study", "action_type": "send_email"}},
            {"id": "action-4", "type": "action", "position": {"x": 400, "y": 500},
             "data": {"label": "Send Re-engagement", "action_type": "send_email"}},
        ],
        "edges": [
            {"id": "e1", "source": "trigger-1", "target": "action-1"},
            {"id": "e2", "source": "action-1", "target": "action-2"},
            {"id": "e3", "source": "action-2", "target": "delay-1"},
            {"id": "e4", "source": "delay-1", "target": "condition-1"},
            {"id": "e5", "source": "condition-1", "target": "action-3", "label": "Yes"},
            {"id": "e6", "source": "condition-1", "target": "action-4", "label": "No"},
        ],
    },
}


@router.get("/templates")
async def get_flow_templates(
    current_user: User = Depends(get_current_user)
):
    """Get available flow templates."""
    return {
        "templates": [
            {
                "id": key,
                "name": template["name"],
                "description": template["description"],
                "node_count": len(template["nodes"]),
            }
            for key, template in FLOW_TEMPLATES.items()
        ]
    }


@router.get("/templates/{template_id}")
async def get_flow_template(
    template_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific flow template."""
    if template_id not in FLOW_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    return FLOW_TEMPLATES[template_id]


@router.post("/", response_model=FlowResponse, status_code=status.HTTP_201_CREATED)
async def create_flow(
    flow_in: FlowCreate,
    org_id: UUID = Query(..., description="Organization ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new automation flow."""
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
    
    # For now, return mock response (DB model integration pending)
    from datetime import datetime
    return FlowResponse(
        id=str(UUID(int=0)),
        name=flow_in.name,
        description=flow_in.description,
        status="draft",
        nodes=[n.model_dump() for n in flow_in.nodes],
        edges=[e.model_dump() for e in flow_in.edges],
        total_executions=0,
        successful_executions=0,
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )


@router.get("/")
async def list_flows(
    org_id: UUID = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all flows for an organization."""
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
    
    # Return empty list for now (DB integration pending)
    return {"flows": [], "total": 0}


@router.get("/node-types")
async def get_node_types(
    current_user: User = Depends(get_current_user)
):
    """Get available node types for the flow builder."""
    return {
        "node_types": [
            {
                "type": "trigger",
                "label": "Trigger",
                "description": "Start the flow based on an event",
                "color": "#10B981",
                "options": [
                    {"id": "form_submit", "label": "Form Submission"},
                    {"id": "page_visit", "label": "Page Visit"},
                    {"id": "cart_abandoned", "label": "Cart Abandoned"},
                    {"id": "purchase", "label": "Purchase Made"},
                    {"id": "lead_created", "label": "New Lead"},
                    {"id": "tag_added", "label": "Tag Added"},
                    {"id": "scheduled", "label": "Scheduled Time"},
                ],
            },
            {
                "type": "action",
                "label": "Action",
                "description": "Perform an action",
                "color": "#0066FF",
                "options": [
                    {"id": "send_email", "label": "Send Email"},
                    {"id": "send_sms", "label": "Send SMS"},
                    {"id": "add_tag", "label": "Add Tag"},
                    {"id": "remove_tag", "label": "Remove Tag"},
                    {"id": "update_field", "label": "Update Field"},
                    {"id": "create_task", "label": "Create Task"},
                    {"id": "webhook", "label": "Send Webhook"},
                    {"id": "crm_add", "label": "Add to CRM"},
                    {"id": "slack_notify", "label": "Slack Notification"},
                ],
            },
            {
                "type": "condition",
                "label": "Condition",
                "description": "Branch based on a condition",
                "color": "#F59E0B",
                "options": [
                    {"id": "email_opened", "label": "Email Opened"},
                    {"id": "email_clicked", "label": "Link Clicked"},
                    {"id": "tag_exists", "label": "Has Tag"},
                    {"id": "field_value", "label": "Field Value"},
                    {"id": "cart_status", "label": "Cart Status"},
                    {"id": "purchase_history", "label": "Purchase History"},
                ],
            },
            {
                "type": "delay",
                "label": "Delay",
                "description": "Wait for a period of time",
                "color": "#8B5CF6",
                "options": [
                    {"id": "fixed", "label": "Fixed Duration"},
                    {"id": "until_time", "label": "Until Specific Time"},
                    {"id": "until_day", "label": "Until Day of Week"},
                ],
            },
            {
                "type": "split",
                "label": "A/B Split",
                "description": "Split traffic for testing",
                "color": "#EC4899",
                "options": [
                    {"id": "random", "label": "Random Split"},
                    {"id": "percentage", "label": "Percentage Based"},
                ],
            },
            {
                "type": "end",
                "label": "End",
                "description": "End the flow",
                "color": "#6B7280",
                "options": [],
            },
        ]
    }

