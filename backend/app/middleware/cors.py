"""
CORS Configuration
Cross-Origin Resource Sharing settings for frontend-backend communication
"""

from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def configure_cors(app):
    """
    Configure CORS middleware for the application.

    In production, this should be configured to only allow
    your frontend domain(s).
    """

    # Determine allowed origins based on environment
    if settings.ENVIRONMENT == "development":
        # In development, allow localhost with various ports
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:5173",  # Vite default
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8080",
        ]
    elif settings.ENVIRONMENT == "staging":
        # Staging environment origins
        allowed_origins = [
            "https://staging.stumpf.works",
            "https://pos-staging.stumpf.works",
        ]
    else:  # production
        # Production - only allow specific domains
        allowed_origins = (
            settings.ALLOWED_ORIGINS.split(",")
            if hasattr(settings, "ALLOWED_ORIGINS")
            else [
                "https://pos.stumpf.works",
                "https://app.stumpf.works",
            ]
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Tenant-ID",
            "X-Request-ID",
            "Accept",
            "Origin",
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-Request-ID",
        ],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    return app
