"""
NeuroCron Security Module
JWT authentication and password hashing
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
import bcrypt

from app.core.config import settings


class TokenPayload(BaseModel):
    """JWT token payload structure"""
    sub: str
    exp: datetime
    type: str = "access"
    org_id: Optional[str] = None


def create_access_token(
    subject: str,
    org_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "access",
        "org_id": org_id,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT refresh token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenPayload(**payload)
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash using bcrypt directly"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')
