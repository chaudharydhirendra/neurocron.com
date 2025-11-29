"""
NeuroCron Dependencies
FastAPI dependency injection
"""

from typing import Generator, Optional, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from redis import asyncio as aioredis

from app.core.config import settings
from app.core.security import decode_token, TokenPayload
from app.models.base import async_session_maker


# Security scheme
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> aioredis.Redis:
    """Get Redis connection"""
    redis = await aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )
    try:
        yield redis
    finally:
        await redis.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    if payload.type != "access":
        raise credentials_exception
    
    # Here we would fetch the user from database
    # For now, return the payload
    return {
        "id": payload.sub,
        "org_id": payload.org_id,
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """Ensure user is active"""
    # Add active check logic here
    return current_user


def require_role(allowed_roles: list[str]):
    """Role-based access control dependency"""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        # Add role checking logic here
        user_role = current_user.get("role", "member")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

