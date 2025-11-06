"""
Rate Limiting Middleware
Prevents API abuse by limiting requests per time window
"""

from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class RateLimiter:
    """
    Token bucket rate limiter
    """

    def __init__(self):
        # Store: {identifier: {"tokens": int, "last_update": datetime}}
        self.buckets = defaultdict(lambda: {
            "tokens": 0,
            "last_update": datetime.now()
        })
        self.cleanup_task = None

    def get_tokens(
        self,
        identifier: str,
        max_tokens: int,
        refill_rate: float
    ) -> tuple[bool, int]:
        """
        Check if request is allowed and return remaining tokens.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens per second

        Returns:
            (is_allowed, remaining_tokens)
        """
        now = datetime.now()
        bucket = self.buckets[identifier]

        # Calculate token refill
        time_passed = (now - bucket["last_update"]).total_seconds()
        bucket["tokens"] = min(
            max_tokens,
            bucket["tokens"] + (time_passed * refill_rate)
        )
        bucket["last_update"] = now

        # Check if request is allowed
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, int(bucket["tokens"])
        else:
            return False, 0

    async def cleanup_old_entries(self):
        """Periodically clean up old bucket entries."""
        while True:
            await asyncio.sleep(3600)  # Run every hour
            now = datetime.now()
            expired = []

            for identifier, bucket in self.buckets.items():
                if (now - bucket["last_update"]).total_seconds() > 3600:
                    expired.append(identifier)

            for identifier in expired:
                del self.buckets[identifier]

            if expired:
                logger.info("rate_limiter_cleanup", removed_count=len(expired))


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware:
    """
    Middleware for rate limiting requests.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        self.app = app
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.refill_rate = requests_per_minute / 60.0  # tokens per second

    async def __call__(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/readiness"]:
            return await call_next(request)

        # Get identifier (prefer user ID, fallback to IP)
        identifier = self._get_identifier(request)

        # Check rate limit
        allowed, remaining = rate_limiter.get_tokens(
            identifier,
            max_tokens=self.burst_size,
            refill_rate=self.refill_rate
        )

        if not allowed:
            logger.warning(
                "rate_limit_exceeded",
                identifier=identifier,
                path=request.url.path
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Try to get user ID from request state (set by auth middleware)
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"

        # Fallback to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP from X-Forwarded-For
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"


# Different rate limits for different endpoints
class EndpointRateLimits:
    """
    Define different rate limits for different endpoint patterns.
    """

    LIMITS = {
        # Aggressive rate limits for auth endpoints
        "/api/v1/auth/login": {"requests_per_minute": 5, "burst_size": 3},
        "/api/v1/auth/register": {"requests_per_minute": 3, "burst_size": 2},

        # Moderate limits for write operations
        "/api/v1/transactions": {"requests_per_minute": 30, "burst_size": 10},
        "/api/v1/products": {"requests_per_minute": 60, "burst_size": 20},

        # Generous limits for read operations
        "/api/v1/products/": {"requests_per_minute": 120, "burst_size": 30},

        # Admin endpoints
        "/api/v1/admin": {"requests_per_minute": 60, "burst_size": 20},

        # Export endpoints (expensive operations)
        "/api/v1/exports": {"requests_per_minute": 10, "burst_size": 2},
    }

    @classmethod
    def get_limit(cls, path: str) -> dict:
        """Get rate limit config for a path."""
        # Check for exact match
        if path in cls.LIMITS:
            return cls.LIMITS[path]

        # Check for prefix match
        for pattern, limits in cls.LIMITS.items():
            if path.startswith(pattern):
                return limits

        # Default limits
        return {"requests_per_minute": 60, "burst_size": 10}
