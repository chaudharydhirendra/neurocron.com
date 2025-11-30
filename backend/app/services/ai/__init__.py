"""
NeuroCron AI Service Layer
Unified AI interface for all platform modules

Tiered Architecture:
- Tier 1 (Strategic): Claude Opus 4.5 - Strategy, competitor analysis, decisions
- Tier 2 (Creative): GPT-4.1 - Ideas, ads, personas, content writing  
- Tier 3 (Standard): Llama 3.1:8b - Social, email, chat, translations (FREE)
"""

from .generator import AIGenerator, AIResponse, AITier, ai_generator
from .prompts import PromptTemplates

__all__ = [
    "AIGenerator",
    "AIResponse", 
    "AITier",
    "ai_generator",
    "PromptTemplates",
]

