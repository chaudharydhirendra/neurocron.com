"""
NeuroCron NeuroCopilot API
Conversational AI command center
"""

from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.copilot.engine import CopilotEngine

router = APIRouter()


class ChatMessage(BaseModel):
    """Chat message schema"""
    content: str
    org_id: Optional[UUID] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response schema"""
    message: str
    actions: Optional[List[dict]] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[dict] = None


class ConversationHistory(BaseModel):
    """Conversation history item"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a message to NeuroCopilot and get a response.
    
    NeuroCopilot can:
    - Answer questions about your marketing data
    - Execute actions like creating campaigns
    - Generate content and strategies
    - Provide insights and recommendations
    
    Example prompts:
    - "Create a Black Friday campaign for $5000 budget"
    - "Why did my CTR drop last week?"
    - "Generate 5 social media post ideas for our product launch"
    - "What's the best performing channel this month?"
    """
    try:
        engine = CopilotEngine(
            user_id=str(current_user.id),
            org_id=str(message.org_id) if message.org_id else None,
            db=db,
        )
        
        response = await engine.process_message(
            message=message.content,
            context=message.context,
        )
        
        return ChatResponse(
            message=response["message"],
            actions=response.get("actions"),
            suggestions=response.get("suggestions"),
            metadata=response.get("metadata"),
        )
    except Exception as e:
        # Log error and return user-friendly message
        return ChatResponse(
            message="I encountered an issue processing your request. Please try again or rephrase your question.",
            metadata={"error": str(e)},
        )


@router.websocket("/ws")
async def websocket_chat(
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat with NeuroCopilot.
    
    Enables streaming responses and real-time updates.
    """
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # Process message
            engine = CopilotEngine(
                user_id=data.get("user_id"),
                org_id=data.get("org_id"),
                db=db,
            )
            
            # Stream response
            async for chunk in engine.stream_response(data.get("message", "")):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk,
                })
            
            await websocket.send_json({
                "type": "complete",
            })
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e),
        })


@router.get("/suggestions")
async def get_suggestions(
    current_user: User = Depends(get_current_user)
):
    """
    Get contextual suggestions for what to ask NeuroCopilot.
    
    Based on user's current state and recent activity.
    """
    return {
        "suggestions": [
            "Create a new campaign for product launch",
            "Analyze my last week's performance",
            "Generate content ideas for social media",
            "Show me competitor insights",
            "Optimize my current campaigns",
            "Create an audience persona",
            "Run a marketing audit",
            "Forecast next month's results",
        ]
    }


@router.get("/history")
async def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """
    Get recent conversation history with NeuroCopilot.
    """
    # TODO: Implement conversation history storage
    return {
        "conversations": [],
        "message": "Conversation history coming soon"
    }


@router.delete("/history")
async def clear_history(
    current_user: User = Depends(get_current_user)
):
    """
    Clear conversation history.
    """
    return {"message": "History cleared"}


class ActionExecute(BaseModel):
    """Execute action request"""
    action_id: str
    org_id: Optional[UUID] = None


@router.post("/execute-action")
async def execute_action(
    action: ActionExecute,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute a confirmed action from NeuroCopilot.
    """
    # In production, this would validate and execute the action
    return {
        "success": True,
        "action_id": action.action_id,
        "message": "Action executed successfully",
        "result": {
            "redirect": "/dashboard",
        }
    }


@router.get("/capabilities")
async def get_capabilities(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of NeuroCopilot capabilities and available actions.
    """
    return {
        "capabilities": [
            {
                "id": "campaigns",
                "name": "Campaign Management",
                "description": "Create, edit, and manage marketing campaigns",
                "actions": ["CREATE_CAMPAIGN", "EDIT_CAMPAIGN", "ANALYZE_CAMPAIGN"],
                "example_prompts": [
                    "Create a new campaign for Black Friday",
                    "What's my best performing campaign?",
                    "Pause all underperforming campaigns",
                ],
            },
            {
                "id": "content",
                "name": "Content Generation",
                "description": "Generate all types of marketing content",
                "actions": ["CREATE_CONTENT", "GENERATE_IDEAS"],
                "example_prompts": [
                    "Write 5 social media posts for our product",
                    "Create a blog article about AI marketing",
                    "Generate email subject lines for our newsletter",
                ],
            },
            {
                "id": "audiences",
                "name": "Audience Intelligence",
                "description": "Create personas and understand your audience",
                "actions": ["GENERATE_PERSONA", "ANALYZE_AUDIENCE"],
                "example_prompts": [
                    "Create a persona for our target customer",
                    "What demographics engage most with our content?",
                    "Segment my audience by behavior",
                ],
            },
            {
                "id": "analytics",
                "name": "Performance Analytics",
                "description": "Analyze and understand your marketing performance",
                "actions": ["ANALYZE_PERFORMANCE", "GENERATE_REPORT"],
                "example_prompts": [
                    "Why did my CTR drop last week?",
                    "Compare this month to last month",
                    "What's driving my conversions?",
                ],
            },
            {
                "id": "automation",
                "name": "Marketing Automation",
                "description": "Create and manage automation flows",
                "actions": ["CREATE_FLOW", "SCHEDULE_POST"],
                "example_prompts": [
                    "Create a welcome email sequence",
                    "Set up abandoned cart recovery",
                    "Schedule posts for next week",
                ],
            },
            {
                "id": "strategy",
                "name": "Strategy & Planning",
                "description": "Generate strategies and marketing plans",
                "actions": ["GENERATE_STRATEGY", "RUN_AUDIT"],
                "example_prompts": [
                    "Create a 12-month marketing strategy",
                    "Audit my current marketing setup",
                    "What should I focus on this quarter?",
                ],
            },
        ]
    }

