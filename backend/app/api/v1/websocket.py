"""
NeuroCron WebSocket API
Real-time notifications and updates
"""

import json
import asyncio
from typing import Dict, Set, Optional
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from jose import JWTError
import logging

from app.core.security import decode_token

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Map of user_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of org_id -> set of user_ids
        self.org_members: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, org_id: Optional[str] = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        if org_id:
            if org_id not in self.org_members:
                self.org_members[org_id] = set()
            self.org_members[org_id].add(user_id)
        
        logger.info(f"WebSocket connected: user={user_id}, org={org_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str, org_id: Optional[str] = None):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Don't remove from org_members as user might reconnect
        logger.info(f"WebSocket disconnected: user={user_id}")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up disconnected
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_to_org(self, message: dict, org_id: str):
        """Broadcast a message to all members of an organization"""
        if org_id in self.org_members:
            for user_id in self.org_members[org_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    org_id: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time notifications.
    
    Connect with: ws://api.neurocron.com/api/v1/ws/ws?token=<jwt_token>&org_id=<org_id>
    """
    # Verify token
    try:
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid token")
            return
        user_id = payload.sub
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return
    
    await manager.connect(websocket, user_id, org_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "user_id": user_id,
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive message (ping/pong or commands)
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # 60 second timeout
                )
                
                try:
                    message = json.loads(data)
                    
                    # Handle ping
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                    
                    # Handle subscribe/unsubscribe to channels
                    elif message.get("type") == "subscribe":
                        channel = message.get("channel")
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel,
                        })
                    
                except json.JSONDecodeError:
                    pass
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, org_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id, org_id)


# Helper functions to send notifications from other parts of the app

async def notify_user(user_id: str, notification: dict):
    """Send a notification to a specific user"""
    await manager.send_personal_message({
        "type": "notification",
        "data": notification,
    }, user_id)


async def notify_org(org_id: str, notification: dict):
    """Send a notification to all members of an organization"""
    await manager.broadcast_to_org({
        "type": "notification",
        "data": notification,
    }, org_id)


async def notify_campaign_update(org_id: str, campaign_id: str, update: dict):
    """Notify about campaign updates"""
    await manager.broadcast_to_org({
        "type": "campaign_update",
        "campaign_id": campaign_id,
        "data": update,
    }, org_id)


async def notify_new_message(org_id: str, message: dict):
    """Notify about new inbox messages"""
    await manager.broadcast_to_org({
        "type": "inbox_message",
        "data": message,
    }, org_id)


async def notify_crisis_alert(org_id: str, alert: dict):
    """Notify about brand crisis alerts"""
    await manager.broadcast_to_org({
        "type": "crisis_alert",
        "priority": "high",
        "data": alert,
    }, org_id)


async def notify_trend_alert(org_id: str, trend: dict):
    """Notify about trending topics"""
    await manager.broadcast_to_org({
        "type": "trend_alert",
        "data": trend,
    }, org_id)

