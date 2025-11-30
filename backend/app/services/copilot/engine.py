"""
NeuroCopilot Engine
The conversational AI that powers the entire platform
"""

from typing import Optional, Dict, Any, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
import json
import uuid

from app.core.config import settings


class CopilotAction:
    """Represents an action that NeuroCopilot can execute"""
    
    def __init__(
        self,
        action_type: str,
        name: str,
        description: str,
        parameters: Dict[str, Any] = None,
        requires_confirmation: bool = True,
    ):
        self.id = str(uuid.uuid4())
        self.action_type = action_type
        self.name = name
        self.description = description
        self.parameters = parameters or {}
        self.requires_confirmation = requires_confirmation
        self.status = "pending"  # pending, confirmed, executed, cancelled
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "action_type": self.action_type,
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_confirmation": self.requires_confirmation,
            "status": self.status,
        }


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

You have access to the following modules and can execute actions:
- NeuroPlan: Strategy generation - create 12-month marketing roadmaps
- AudienceGenome: Customer personas - generate and manage audience segments
- BrainSpark: Creative ideas - generate campaign concepts and content ideas
- AutoCron: Task execution - schedule and automate marketing tasks
- ContentForge: Content creation - generate blogs, social posts, ads, emails
- AdPilot: Ad management - create and optimize ad campaigns
- FlowBuilder: Automation - build customer journey flows
- AuditX: Marketing audits - comprehensive marketing health checks
- InsightCortex: Analytics - performance dashboards and reports

When users ask for actions, you can execute them directly. Available actions:
- CREATE_CAMPAIGN: Create a new marketing campaign
- CREATE_CONTENT: Generate content (specify type: social, blog, email, ad)
- CREATE_AD: Create an ad creative with copy and targeting
- GENERATE_PERSONA: Create a customer persona
- GENERATE_STRATEGY: Create a marketing strategy
- RUN_AUDIT: Start a marketing audit
- GENERATE_IDEAS: Brainstorm creative marketing ideas
- CREATE_FLOW: Create an automation flow
- SCHEDULE_POST: Schedule a social media post
- ANALYZE_PERFORMANCE: Generate performance analysis

When you want to execute an action, include it in your response using this format:
[ACTION:ACTION_TYPE|param1=value1|param2=value2]

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
        self.pending_actions: List[CopilotAction] = []
    
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
        actions = self._extract_actions(response, intent, message)
        
        # Clean response of action markers
        clean_response = self._clean_response(response)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(intent, message)
        
        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": clean_response,
        })
        
        return {
            "message": clean_response,
            "actions": [a.to_dict() for a in actions] if actions else [],
            "suggestions": suggestions,
            "metadata": {
                "intent": intent,
                "org_id": self.org_id,
                "actions_pending": len([a for a in actions if a.requires_confirmation]) if actions else 0,
            }
        }
    
    async def execute_action(
        self,
        action_id: str,
    ) -> Dict[str, Any]:
        """Execute a confirmed action."""
        # Find the action
        action = next((a for a in self.pending_actions if a.id == action_id), None)
        if not action:
            return {"success": False, "error": "Action not found"}
        
        try:
            result = await self._execute_action_by_type(action)
            action.status = "executed"
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_action_by_type(self, action: CopilotAction) -> Dict[str, Any]:
        """Execute action based on its type."""
        action_handlers = {
            "CREATE_CAMPAIGN": self._action_create_campaign,
            "CREATE_CONTENT": self._action_create_content,
            "CREATE_AD": self._action_create_ad,
            "GENERATE_PERSONA": self._action_generate_persona,
            "GENERATE_STRATEGY": self._action_generate_strategy,
            "RUN_AUDIT": self._action_run_audit,
            "GENERATE_IDEAS": self._action_generate_ideas,
            "CREATE_FLOW": self._action_create_flow,
            "SCHEDULE_POST": self._action_schedule_post,
            "ANALYZE_PERFORMANCE": self._action_analyze_performance,
        }
        
        handler = action_handlers.get(action.action_type)
        if handler:
            return await handler(action.parameters)
        
        return {"message": f"Action {action.action_type} executed successfully"}
    
    async def _action_create_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new campaign."""
        return {
            "message": "Campaign created successfully",
            "campaign_id": str(uuid.uuid4()),
            "name": params.get("name", "New Campaign"),
            "redirect": "/dashboard/campaigns",
        }
    
    async def _action_create_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content."""
        content_type = params.get("type", "social")
        return {
            "message": f"Generated {content_type} content",
            "content_id": str(uuid.uuid4()),
            "type": content_type,
            "redirect": "/content",
        }
    
    async def _action_create_ad(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an ad."""
        return {
            "message": "Ad creative generated",
            "ad_id": str(uuid.uuid4()),
            "redirect": "/ads",
        }
    
    async def _action_generate_persona(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a customer persona."""
        return {
            "message": "Persona generated",
            "persona_id": str(uuid.uuid4()),
            "redirect": "/audiences",
        }
    
    async def _action_generate_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a marketing strategy."""
        return {
            "message": "Strategy generated",
            "strategy_id": str(uuid.uuid4()),
            "redirect": "/strategy",
        }
    
    async def _action_run_audit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a marketing audit."""
        return {
            "message": "Audit started",
            "audit_id": str(uuid.uuid4()),
            "redirect": "/audit",
        }
    
    async def _action_generate_ideas(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate creative ideas."""
        return {
            "message": "Ideas generated",
            "count": 5,
            "redirect": "/strategy",
        }
    
    async def _action_create_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an automation flow."""
        return {
            "message": "Flow created",
            "flow_id": str(uuid.uuid4()),
            "redirect": "/flows",
        }
    
    async def _action_schedule_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a social post."""
        return {
            "message": "Post scheduled",
            "post_id": str(uuid.uuid4()),
            "redirect": "/inbox",
        }
    
    async def _action_analyze_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance."""
        return {
            "message": "Analysis complete",
            "report_id": str(uuid.uuid4()),
            "redirect": "/analytics",
        }
    
    async def stream_response(
        self,
        message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream response tokens for real-time chat experience.
        """
        # Add message to history
        self.conversation_history.append({
            "role": "user",
            "content": message,
        })
        
        full_response = ""
        
        # Try Ollama first (local), then fall back to OpenAI
        try:
            async for chunk in self._stream_ollama(message):
                full_response += chunk
                yield chunk
        except Exception:
            try:
                async for chunk in self._stream_openai(message):
                    full_response += chunk
                    yield chunk
            except Exception:
                # Fallback to non-streaming
                response = self._generate_fallback_response(message)
                yield response
                full_response = response
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": self._clean_response(full_response),
        })
    
    def _detect_intent(self, message: str) -> str:
        """Detect the user's intent from their message."""
        message_lower = message.lower()
        
        # Intent detection based on keywords
        if any(word in message_lower for word in ["create", "launch", "start", "new", "make", "build"]):
            if "campaign" in message_lower:
                return "create_campaign"
            if "content" in message_lower or "post" in message_lower or "article" in message_lower:
                return "create_content"
            if "ad" in message_lower or "advertisement" in message_lower:
                return "create_ad"
            if "persona" in message_lower or "audience" in message_lower:
                return "create_persona"
            if "flow" in message_lower or "automation" in message_lower:
                return "create_flow"
            if "strategy" in message_lower:
                return "create_strategy"
        
        if any(word in message_lower for word in ["analyze", "analysis", "performance", "metrics", "report"]):
            return "analyze"
        
        if any(word in message_lower for word in ["why", "explain", "what happened", "tell me about"]):
            return "explain"
        
        if any(word in message_lower for word in ["suggest", "recommend", "ideas", "brainstorm"]):
            return "suggest"
        
        if any(word in message_lower for word in ["audit", "check", "review", "health"]):
            return "audit"
        
        if any(word in message_lower for word in ["forecast", "predict", "future", "project"]):
            return "forecast"
        
        if any(word in message_lower for word in ["schedule", "post", "publish"]):
            return "schedule"
        
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
            *self.conversation_history[-10:],
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
                timeout=120.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue
    
    async def _stream_openai(self, message: str) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI."""
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            *self.conversation_history[-10:],
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
                timeout=120.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[6:])
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
    
    def _generate_fallback_response(self, message: str) -> str:
        """Generate a response when AI is unavailable."""
        intent = self._detect_intent(message)
        
        responses = {
            "create_campaign": "I'd be happy to help you create a campaign! 🚀\n\nTo get started, I'll need:\n\n1. **Campaign name** - What would you like to call it?\n2. **Objective** - Awareness, leads, or sales?\n3. **Target audience** - Who are we reaching?\n4. **Budget** - What's your daily/monthly budget?\n5. **Channels** - Google, Meta, LinkedIn?\n\nWould you like me to guide you through this step by step, or shall I use a template from LaunchPad?",
            "create_content": "I can help you create content! ✍️\n\nWhat type would you like?\n\n• **Social posts** - Engaging content for your channels\n• **Blog articles** - SEO-optimized long-form content\n• **Email newsletters** - Campaigns that convert\n• **Ad copy** - High-converting ad creatives\n• **Landing pages** - Conversion-focused pages\n\nTell me more about your topic and target audience, and I'll generate some options!",
            "create_persona": "Let's create a customer persona! 🎯\n\nI'll need to know:\n\n1. Your industry/business type\n2. Your products or services\n3. Your target market\n4. Any existing customer data you have\n\nWith this info, I'll generate detailed personas including demographics, psychographics, pain points, and buying triggers.",
            "analyze": "I can analyze your marketing performance! 📊\n\nWhat would you like me to look at?\n\n• **Campaign performance** - ROI, conversions, spend\n• **Channel comparison** - Which channels work best\n• **Audience insights** - Who's engaging\n• **Content performance** - Top-performing content\n• **Trend analysis** - What's changing over time\n\nSelect an area and I'll dive deep!",
            "audit": "I can run a comprehensive marketing audit! 🔍\n\nThis covers:\n\n• **Website & SEO** - Speed, structure, rankings\n• **Ad accounts** - Health scores, opportunities\n• **Social profiles** - Engagement, growth\n• **Content quality** - Performance metrics\n• **Funnel analysis** - Drop-off points\n\nShall I start the audit now?",
            "suggest": "Here are some marketing ideas for you! 💡\n\n1. **Content Idea**: Create a series of educational posts addressing common pain points\n2. **Campaign Idea**: Run a limited-time offer with urgency messaging\n3. **Engagement Idea**: Host a live Q&A session with your audience\n4. **Growth Hack**: Partner with complementary brands for cross-promotion\n5. **Retention**: Launch a loyalty program with exclusive benefits\n\nWould you like me to expand on any of these?",
            "general": "I'm NeuroCopilot, your AI marketing assistant! 🧠\n\nI can help you with:\n\n• **Create** - Campaigns, content, ads, personas\n• **Analyze** - Performance, trends, audiences\n• **Automate** - Flows, schedules, tasks\n• **Optimize** - Improve what's working\n• **Audit** - Check your marketing health\n\nWhat would you like to work on today?",
        }
        
        return responses.get(intent, responses["general"])
    
    def _clean_response(self, response: str) -> str:
        """Remove action markers from response for display."""
        import re
        # Remove [ACTION:...] markers
        cleaned = re.sub(r'\[ACTION:[^\]]+\]', '', response)
        return cleaned.strip()
    
    def _extract_actions(
        self,
        response: str,
        intent: str,
        message: str,
    ) -> List[CopilotAction]:
        """Extract actionable items from the response."""
        import re
        actions = []
        
        # Parse [ACTION:TYPE|param=value] markers
        action_pattern = r'\[ACTION:([A-Z_]+)(?:\|([^\]]+))?\]'
        matches = re.findall(action_pattern, response)
        
        for match in matches:
            action_type = match[0]
            params_str = match[1] if len(match) > 1 else ""
            
            # Parse parameters
            params = {}
            if params_str:
                for param in params_str.split("|"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        params[key.strip()] = value.strip()
            
            action = CopilotAction(
                action_type=action_type,
                name=self._get_action_name(action_type),
                description=self._get_action_description(action_type, params),
                parameters=params,
                requires_confirmation=True,
            )
            actions.append(action)
            self.pending_actions.append(action)
        
        # If no explicit actions but intent suggests one, create suggestion
        if not actions and intent in ["create_campaign", "create_content", "audit"]:
            intent_to_action = {
                "create_campaign": "CREATE_CAMPAIGN",
                "create_content": "CREATE_CONTENT",
                "audit": "RUN_AUDIT",
            }
            action_type = intent_to_action.get(intent)
            if action_type:
                action = CopilotAction(
                    action_type=action_type,
                    name=self._get_action_name(action_type),
                    description=self._get_action_description(action_type, {}),
                    parameters={},
                    requires_confirmation=True,
                )
                actions.append(action)
                self.pending_actions.append(action)
        
        return actions
    
    def _get_action_name(self, action_type: str) -> str:
        """Get human-readable name for action type."""
        names = {
            "CREATE_CAMPAIGN": "Create Campaign",
            "CREATE_CONTENT": "Generate Content",
            "CREATE_AD": "Create Ad",
            "GENERATE_PERSONA": "Generate Persona",
            "GENERATE_STRATEGY": "Create Strategy",
            "RUN_AUDIT": "Run Audit",
            "GENERATE_IDEAS": "Generate Ideas",
            "CREATE_FLOW": "Create Flow",
            "SCHEDULE_POST": "Schedule Post",
            "ANALYZE_PERFORMANCE": "Analyze Performance",
        }
        return names.get(action_type, action_type.replace("_", " ").title())
    
    def _get_action_description(self, action_type: str, params: Dict[str, Any]) -> str:
        """Get description for action."""
        descriptions = {
            "CREATE_CAMPAIGN": "Create a new marketing campaign",
            "CREATE_CONTENT": f"Generate {params.get('type', 'content')}",
            "CREATE_AD": "Create an ad creative",
            "GENERATE_PERSONA": "Generate a customer persona",
            "GENERATE_STRATEGY": "Create a marketing strategy",
            "RUN_AUDIT": "Run a comprehensive marketing audit",
            "GENERATE_IDEAS": "Generate creative marketing ideas",
            "CREATE_FLOW": "Create an automation flow",
            "SCHEDULE_POST": "Schedule a social media post",
            "ANALYZE_PERFORMANCE": "Generate a performance analysis report",
        }
        return descriptions.get(action_type, f"Execute {action_type}")
    
    def _generate_suggestions(self, intent: str, message: str) -> List[str]:
        """Generate follow-up suggestions based on intent."""
        suggestions_map = {
            "create_campaign": [
                "Use a template from LaunchPad",
                "Let me generate a strategy first",
                "Show me similar past campaigns",
                "Help me define my target audience",
            ],
            "create_content": [
                "Generate multiple variations",
                "Optimize for specific audience",
                "Schedule for best engagement times",
                "Create a content calendar",
            ],
            "create_persona": [
                "Generate multiple personas",
                "Add behavioral triggers",
                "Create customer journey map",
            ],
            "analyze": [
                "Compare to previous period",
                "Show competitor benchmarks",
                "Predict next month's performance",
                "Export as PDF report",
            ],
            "audit": [
                "Focus on SEO only",
                "Include competitor analysis",
                "Schedule recurring audits",
            ],
            "general": [
                "Run a marketing audit",
                "Create a new campaign",
                "Generate content ideas",
                "Analyze recent performance",
            ],
        }
        
        return suggestions_map.get(intent, suggestions_map["general"])[:4]
