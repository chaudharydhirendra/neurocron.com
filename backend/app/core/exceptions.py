"""
NeuroCron Custom Exceptions
Centralized error handling
"""

from fastapi import HTTPException, status


class NeuroCronException(HTTPException):
    """Base exception for NeuroCron"""
    pass


class AuthenticationError(NeuroCronException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(NeuroCronException):
    """Authorization failed - insufficient permissions"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class NotFoundError(NeuroCronException):
    """Resource not found"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found"
        )


class ValidationError(NeuroCronException):
    """Validation failed"""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class ConflictError(NeuroCronException):
    """Resource conflict (e.g., duplicate)"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class RateLimitError(NeuroCronException):
    """Rate limit exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )


class ExternalServiceError(NeuroCronException):
    """External service (API) error"""
    def __init__(self, service: str, detail: str = "Service unavailable"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service}: {detail}"
        )

