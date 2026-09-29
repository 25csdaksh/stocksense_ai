"""
Centralized Exceptions & Global Exception Handlers for MarketMind AI.
"""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import logger


class MarketMindException(Exception):
    """Base exception for all domain-specific MarketMind AI errors."""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ResourceNotFoundException(MarketMindException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} '{identifier}' not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)}
        )


class ProviderException(MarketMindException):
    def __init__(self, provider_name: str, reason: str):
        super().__init__(
            message=f"External data provider '{provider_name}' error: {reason}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"provider": provider_name, "reason": reason}
        )


class ValidationException(MarketMindException):
    def __init__(self, message: str, errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"errors": errors or {}}
        )


class UnauthorizedException(MarketMindException):
    def __init__(self, message: str = "Invalid or expired authentication credentials."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RateLimitException(MarketMindException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


async def marketmind_exception_handler(request: Request, exc: MarketMindException) -> JSONResponse:
    """Global FastAPI handler for MarketMindException subclasses."""
    logger.warning(f"MarketMindException on {request.method} {request.url.path}: {exc.message} ({exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unhandled exception handler."""
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "status_code": 500,
            "message": "An internal server error occurred.",
            "details": {"error_type": exc.__class__.__name__},
            "path": request.url.path,
        }
    )
