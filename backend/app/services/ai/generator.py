"""
NeuroCron AI Generator
Tiered AI architecture for cost-effective, high-quality generation

Tier 1 (Strategic): Claude Opus 4.5 - Strategy, competitor analysis, business decisions
Tier 2 (Creative): GPT-4.1 - Ideas, ads, personas, content writing
Tier 3 (Standard): Llama 3.1:8b - Social posts, emails, chat, translations (FREE)
"""

from typing import Optional, Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from enum import Enum
import httpx
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class AITier(Enum):
    """AI tier for task routing."""
    STRATEGIC = "strategic"  # Claude Opus 4.5 - complex reasoning
    CREATIVE = "creative"    # GPT-4.1 - creative content
    STANDARD = "standard"    # Llama 3.1 (local, FREE)


@dataclass
class AIResponse:
    """Structured AI response."""
    success: bool
    content: str
    model_used: str
    tier: AITier
    tokens_in: int = 0
    tokens_out: int = 0
    cost_estimate: float = 0.0
    parsed_json: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    @property
    def as_json(self) -> Optional[Dict[str, Any]]:
        """Parse response as JSON if not already parsed."""
        if self.parsed_json:
            return self.parsed_json
        try:
            # Try to extract JSON from the content
            content = self.content.strip()
            # Handle markdown code blocks
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end].strip()
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end].strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return None


class AIGenerator:
    """
    Unified AI generator with tiered model routing.
    
    Routes tasks to the most appropriate (and cost-effective) model:
    - Strategic tasks → Claude Opus 4.5 (best reasoning)
    - Creative tasks → GPT-4.1 (best creative)
    - Standard tasks → Llama 3.1 (FREE, local)
    """
    
    # Pricing per million tokens (as of Nov 2025)
    PRICING = {
        "claude-opus-4-5": {"input": 5.0, "output": 25.0},
        "gpt-4.1": {"input": 10.0, "output": 30.0},
        "llama3.1:8b": {"input": 0.0, "output": 0.0},  # FREE (local)
        "llama3.2:3b": {"input": 0.0, "output": 0.0},  # FREE (local)
    }
    
    # Task to tier mapping
    TASK_TIERS = {
        # Tier 1: Strategic (Claude Opus 4.5)
        "strategy": AITier.STRATEGIC,
        "competitor_analysis": AITier.STRATEGIC,
        "market_analysis": AITier.STRATEGIC,
        "business_decision": AITier.STRATEGIC,
        "audit": AITier.STRATEGIC,
        "forecast": AITier.STRATEGIC,
        
        # Tier 2: Creative (GPT-4.1)
        "creative_ideas": AITier.CREATIVE,
        "ad_copy": AITier.CREATIVE,
        "persona": AITier.CREATIVE,
        "blog_content": AITier.CREATIVE,
        "content_writing": AITier.CREATIVE,
        "campaign_concept": AITier.CREATIVE,
        
        # Tier 3: Standard (Llama 3.1 - FREE)
        "social_post": AITier.STANDARD,
        "email": AITier.STANDARD,
        "translation": AITier.STANDARD,
        "chat": AITier.STANDARD,
        "summarize": AITier.STANDARD,
        "rewrite": AITier.STANDARD,
    }
    
    def __init__(self):
        """Initialize the AI generator."""
        self.ollama_available = True
        self.openai_available = bool(settings.OPENAI_API_KEY)
        self.anthropic_available = bool(settings.ANTHROPIC_API_KEY)
    
    def get_tier_for_task(self, task_type: str) -> AITier:
        """Get the appropriate tier for a task type."""
        return self.TASK_TIERS.get(task_type, AITier.STANDARD)
    
    def get_model_for_tier(self, tier: AITier) -> tuple[str, str]:
        """
        Get the model and provider for a tier.
        Returns (model_name, provider) tuple.
        Falls back to lower tiers if higher tier unavailable.
        """
        if tier == AITier.STRATEGIC:
            if self.anthropic_available:
                return settings.ANTHROPIC_MODEL, "anthropic"
            elif self.openai_available:
                return settings.OPENAI_MODEL, "openai"
            else:
                return settings.OLLAMA_MODEL, "ollama"
        
        elif tier == AITier.CREATIVE:
            if self.openai_available:
                return settings.OPENAI_MODEL, "openai"
            elif self.anthropic_available:
                return settings.ANTHROPIC_MODEL, "anthropic"
            else:
                return settings.OLLAMA_MODEL, "ollama"
        
        else:  # STANDARD
            return settings.OLLAMA_MODEL, "ollama"
    
    def estimate_cost(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
    ) -> float:
        """Estimate cost for a generation."""
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        cost_in = (tokens_in / 1_000_000) * pricing["input"]
        cost_out = (tokens_out / 1_000_000) * pricing["output"]
        return round(cost_in + cost_out, 6)
    
    async def generate(
        self,
        task_type: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        force_tier: Optional[AITier] = None,
    ) -> AIResponse:
        """
        Generate AI content with automatic tier routing.
        
        Args:
            task_type: Type of task (used for tier routing)
            system_prompt: System prompt for the AI
            user_prompt: User prompt with the request
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            force_tier: Override automatic tier selection
        
        Returns:
            AIResponse with the generated content
        """
        tier = force_tier or self.get_tier_for_task(task_type)
        model, provider = self.get_model_for_tier(tier)
        
        logger.info(f"AI Generation: task={task_type}, tier={tier.value}, model={model}")
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            if provider == "anthropic":
                return await self._call_anthropic(messages, model, tier, temperature, max_tokens)
            elif provider == "openai":
                return await self._call_openai(messages, model, tier, temperature, max_tokens)
            else:
                return await self._call_ollama(messages, model, tier, temperature, max_tokens)
        
        except Exception as e:
            logger.error(f"AI Generation failed: {e}")
            # Try fallback to local model
            if provider != "ollama":
                logger.info("Falling back to local Ollama model")
                try:
                    return await self._call_ollama(
                        messages, settings.OLLAMA_MODEL, AITier.STANDARD, temperature, max_tokens
                    )
                except Exception as fallback_error:
                    return AIResponse(
                        success=False,
                        content="",
                        model_used=model,
                        tier=tier,
                        error=f"All AI providers failed. Last error: {fallback_error}",
                    )
            return AIResponse(
                success=False,
                content="",
                model_used=model,
                tier=tier,
                error=str(e),
            )
    
    async def _call_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tier: AITier,
        temperature: float,
        max_tokens: int,
    ) -> AIResponse:
        """Call Anthropic Claude API."""
        # Extract system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "system": system_content,
                    "messages": chat_messages,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["content"][0]["text"]
            tokens_in = data.get("usage", {}).get("input_tokens", 0)
            tokens_out = data.get("usage", {}).get("output_tokens", 0)
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model,
                tier=tier,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_estimate=self.estimate_cost(model, tokens_in, tokens_out),
            )
    
    async def _call_openai(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tier: AITier,
        temperature: float,
        max_tokens: int,
    ) -> AIResponse:
        """Call OpenAI API."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            
            content = data["choices"][0]["message"]["content"]
            tokens_in = data.get("usage", {}).get("prompt_tokens", 0)
            tokens_out = data.get("usage", {}).get("completion_tokens", 0)
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model,
                tier=tier,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_estimate=self.estimate_cost(model, tokens_in, tokens_out),
            )
    
    async def _call_ollama(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tier: AITier,
        temperature: float,
        max_tokens: int,
    ) -> AIResponse:
        """Call local Ollama instance."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
                timeout=180.0,  # Longer timeout for local model
            )
            response.raise_for_status()
            data = response.json()
            
            content = data.get("message", {}).get("content", "")
            # Ollama returns token counts differently
            tokens_in = data.get("prompt_eval_count", 0)
            tokens_out = data.get("eval_count", 0)
            
            return AIResponse(
                success=True,
                content=content,
                model_used=model,
                tier=tier,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_estimate=0.0,  # FREE!
            )
    
    async def stream_generate(
        self,
        task_type: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        """
        Stream AI generation for real-time responses.
        Uses Ollama for streaming (best latency for local).
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": messages,
                    "stream": True,
                    "options": {"temperature": temperature},
                },
                timeout=180.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            continue


# Singleton instance
ai_generator = AIGenerator()

