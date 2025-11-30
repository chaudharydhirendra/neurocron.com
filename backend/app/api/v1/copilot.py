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

