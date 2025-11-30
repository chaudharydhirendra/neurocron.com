"""
NeuroCron Configuration
Centralized settings management using Pydantic
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "NeuroCron"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    
    # URLs
    DOMAIN: str = "neurocron.com"
    API_URL: str = "http://localhost:8100"
    FRONTEND_URL: str = "http://localhost:3100"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3100",
        "http://localhost:3000",
        "https://neurocron.com",
        "https://www.neurocron.com",
    ]
    
    # Database
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "neurocron_db"
    POSTGRES_USER: str = "neurocron"
    POSTGRES_PASSWORD: str = "neurocron_secret"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6380
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    
    # Celery
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"
    
    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"
    
    # MinIO
    MINIO_HOST: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str = "neurocron"
    MINIO_ROOT_PASSWORD: str = "neurocron_minio_secret"
    MINIO_BUCKET: str = "neurocron-assets"
    
    # Meilisearch
    MEILISEARCH_HOST: str = "localhost"
    MEILISEARCH_PORT: int = 7700
    MEILISEARCH_MASTER_KEY: str = "neurocron_search_key"
    
    # AI Services - Tiered Architecture
    # ═══════════════════════════════════════════════════════════════════
    # Tier 1 (Strategic): Claude Opus 4.5 - Best reasoning, $5/$25 per 1M tokens
    # Tier 2 (Creative): GPT-4.1 - Best creative, ~$10/$30 per 1M tokens  
    # Tier 3 (Standard): Llama 3.1:8b - FREE, runs locally
    # ═══════════════════════════════════════════════════════════════════
    
    # Tier 3: Ollama (local, FREE) - Social posts, emails, chat, translations
    OLLAMA_HOST: str = "localhost"
    OLLAMA_PORT: int = 11434
    OLLAMA_MODEL: str = "llama3.1:8b"  # Primary local model (8B params)
    OLLAMA_MODEL_FAST: str = "llama3.2:3b"  # Faster for simple tasks
    
    # Tier 2: OpenAI (PAID) - Creative tasks: ideas, ads, personas, content
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4.1"  # Best for creative content
    
    # Tier 1: Anthropic (PAID) - Strategic tasks: strategy, competitor analysis
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-opus-4-5"  # Best for reasoning & strategy
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "hello@neurocron.com"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Sentry
    SENTRY_DSN: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()

