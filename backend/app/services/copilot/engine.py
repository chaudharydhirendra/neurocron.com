"""
NeuroCopilot Engine
The conversational AI that powers the entire platform
"""

from typing import Optional, Dict, Any, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import json

from app.core.config import settings


class CopilotEngine:
    """
    NeuroCopilot - The conversational AI command center.
    
    Processes natural language commands and routes them to appropriate
    platform modules for execution.
    """
    
    SYSTEM_PROMPT = """You are NeuroCopilot, the AI assistant for NeuroCron - The Autonomous Marketing Brain.

You help users with:
1. Creating and managing marketing campaigns
2. Generating content (social posts, ads, emails, blog articles)
3. Analyzing marketing performance
4. Providing strategic recommendations
5. Executing marketing tasks automatically

You have access to the following modules:
- NeuroPlan: Strategy generation
- AudienceGenome: Customer personas
- BrainSpark: Creative ideas
- AutoCron: Task execution
- ContentForge: Content creation
- AdPilot: Ad management
- AuditX: Marketing audits
- InsightCortex: Analytics

When users ask for actions, respond with:
1. A clear explanation of what you'll do
2. The specific actions to be taken
3. Any follow-up questions if needed

Be concise, helpful, and proactive. Suggest optimizations when you see opportunities.
Always maintain a professional yet friendly tone."""

    def __init__(
        self,
        user_id: str,
        org_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ):
        self.user_id = user_id
        self.org_id = org_id
        self.db = db
        self.conversation_history: List[Dict[str, str]] = []
    
    async def process_message(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        This method:
        1. Analyzes the user's intent
        2. Routes to appropriate module(s)
        3. Executes actions if needed
        4. Returns response with actions taken
        """
        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
        })
        
        # Detect intent and generate response
        intent = self._detect_intent(message)
        
        # Get AI response
        response = await self._get_ai_response(message, context)
        
        # Parse any actions from the response
        actions = self._extract_actions(response, intent)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(intent)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
        })
        
        return {
            "message": response,
            "actions": actions,
            "suggestions": suggestions,
            "metadata": {
                "intent": intent,
                "org_id": self.org_id,
            }
        }
    
    async def stream_response(
        self,
        message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response tokens for real-time chat experience.
        """
        # Try Ollama first (local), then fall back to OpenAI
        try:
            async for chunk in self._stream_ollama(message):
                yield chunk
        except Exception:
            async for chunk in self._stream_openai(message):
                yield chunk
    
    def _detect_intent(self, message: str) -> str:
        """Detect the user's intent from their message."""
        message_lower = message.lower()
        
        # Intent detection based on keywords
        if any(word in message_lower for word in ["create", "launch", "start", "new"]):
            if "campaign" in message_lower:
                return "create_campaign"
            if "content" in message_lower or "post" in message_lower:
                return "create_content"
            if "ad" in message_lower:
                return "create_ad"
        
        if any(word in message_lower for word in ["analyze", "analysis", "performance", "metrics"]):
            return "analyze"
        
        if any(word in message_lower for word in ["why", "explain", "what happened"]):
            return "explain"
        
        if any(word in message_lower for word in ["suggest", "recommend", "ideas"]):
            return "suggest"
        
        if any(word in message_lower for word in ["audit", "check", "review"]):
            return "audit"
        
        if any(word in message_lower for word in ["forecast", "predict", "future"]):
            return "forecast"
        
        return "general"
    
    async def _get_ai_response(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Get AI response using available LLM."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *self.conversation_history[-10:],  # Last 10 messages for context
        ]
        
        # Try Ollama first (local, free)
        try:
            return await self._call_ollama(messages)
        except Exception:
            pass
        
        # Fall back to OpenAI if available
        if settings.OPENAI_API_KEY:
            try:
                return await self._call_openai(messages)
            except Exception:
                pass
        
        # Default response if no AI available
        return self._generate_fallback_response(message)
    
    async def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Call local Ollama instance."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": False,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": messages,
                    "max_tokens": 1000,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    
    async def _stream_ollama(self, message: str) -> AsyncGenerator[str, None]:
        """Stream response from Ollama."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
    
    async def _stream_openai(self, message: str) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.OPENAI_MODEL,
                    "messages": messages,
                    "max_tokens": 1000,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        data = json.loads(line[6:])
                        if "choices" in data and data["choices"]:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                yield delta["content"]
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate a response when AI is unavailable."""
        intent = self._detect_intent(message)
        
        responses = {
            "create_campaign": "I'd be happy to help you create a campaign! To get started, I'll need:\n\n1. Campaign name\n2. Target audience\n3. Budget\n4. Channels (Google, Meta, etc.)\n5. Start and end dates\n\nWould you like me to guide you through this step by step?",
            "create_content": "I can help you create content! What type would you like?\n\n• Social media posts\n• Blog articles\n• Email newsletters\n• Ad copy\n• Landing pages\n\nLet me know and I'll generate some options for you.",
            "analyze": "I can analyze your marketing performance. Would you like me to look at:\n\n• Campaign performance\n• Channel comparison\n• Audience insights\n• Content engagement\n• ROI analysis\n\nSelect an area to dive deeper.",
            "audit": "I can run a comprehensive marketing audit covering:\n\n• Website & SEO\n• Ad accounts health\n• Social presence\n• Content quality\n• Funnel performance\n\nShall I start the audit?",
            "general": "I'm here to help with your marketing! You can ask me to:\n\n• Create campaigns and content\n• Analyze performance\n• Run audits\n• Generate ideas\n• Provide recommendations\n\nWhat would you like to do?",
        }
        
        return responses.get(intent, responses["general"])
    
    def _extract_actions(
        self,
        response: str,
        intent: str,
    ) -> Optional[List[Dict[str, Any]]]:
        """Extract actionable items from the response."""
        # This would parse the AI response for executable actions
        # For now, return None
        return None
    
    def _generate_suggestions(self, intent: str) -> List[str]:
        """Generate follow-up suggestions based on intent."""
        suggestions_map = {
            "create_campaign": [
                "Use a template from LaunchPad",
                "Let me generate a strategy first",
                "Show me similar past campaigns",
            ],
            "create_content": [
                "Generate multiple variations",
                "Optimize for specific audience",
                "Schedule for best engagement times",
            ],
            "analyze": [
                "Compare to previous period",
                "Show competitor benchmarks",
                "Predict next month's performance",
            ],
            "general": [
                "Run a marketing audit",
                "Create a new campaign",
                "Analyze recent performance",
            ],
        }
        
        return suggestions_map.get(intent, suggestions_map["general"])

