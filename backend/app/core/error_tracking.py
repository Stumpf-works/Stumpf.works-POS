"""
Error Tracking Configuration
Sentry integration for production error monitoring
"""

import sentry_sdk
import structlog
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings

logger = structlog.get_logger()


def configure_error_tracking():
    """
    Configure Sentry for error tracking.
    Only enabled in staging/production with SENTRY_DSN set.
    """

    if not settings.SENTRY_DSN:
        logger.info("sentry_disabled", reason="SENTRY_DSN not configured")
        return

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            # Integrations
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
            ],
            # Send default PII (Personally Identifiable Information)
            send_default_pii=False,  # Don't send user data by default
            # Performance monitoring
            enable_tracing=True,
            # Release tracking
            release=f"stumpf-pos@{settings.APP_VERSION}",
            # Before send hook to filter/modify events
            before_send=before_send_hook,
            # Before breadcrumb hook
            before_breadcrumb=before_breadcrumb_hook,
        )

        logger.info(
            "sentry_initialized",
            environment=settings.ENVIRONMENT,
            sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        )

    except Exception as e:
        logger.error("sentry_init_failed", error=str(e), exc_info=True)


def before_send_hook(event, hint):
    """
    Hook called before sending event to Sentry.
    Use this to filter or modify events.
    """

    # Filter out certain exceptions
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Don't send validation errors to Sentry
        if exc_type.__name__ in ["ValidationError", "RequestValidationError"]:
            return None

        # Don't send 404 errors
        if exc_type.__name__ == "HTTPException":
            if hasattr(exc_value, "status_code") and exc_value.status_code == 404:
                return None

    # Scrub sensitive data from event
    if "request" in event:
        request = event["request"]

        # Remove sensitive headers
        if "headers" in request:
            sensitive_headers = ["Authorization", "X-Api-Key", "Cookie"]
            for header in sensitive_headers:
                if header in request["headers"]:
                    request["headers"][header] = "[Filtered]"

        # Remove sensitive query params
        if "query_string" in request:
            # Scrub passwords, tokens, etc.
            pass

    return event


def before_breadcrumb_hook(crumb, hint):
    """
    Hook called before adding breadcrumb.
    Use this to filter or modify breadcrumbs.
    """

    # Don't log sensitive queries
    if crumb.get("category") == "query":
        if "password" in crumb.get("message", "").lower():
            return None

    return crumb


def capture_exception(exception: Exception, **kwargs):
    """
    Manually capture an exception and send to Sentry.

    Args:
        exception: The exception to capture
        **kwargs: Additional context (user, tags, extras, etc.)
    """

    if not settings.SENTRY_DSN:
        # Just log if Sentry not configured
        logger.error(
            "exception_occurred",
            error=str(exception),
            error_type=type(exception).__name__,
            **kwargs,
        )
        return

    with sentry_sdk.push_scope() as scope:
        # Add user context
        if "user" in kwargs:
            user = kwargs.pop("user")
            scope.set_user(
                {
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "email": user.get("email"),
                }
            )

        # Add tags
        if "tags" in kwargs:
            for key, value in kwargs.pop("tags").items():
                scope.set_tag(key, value)

        # Add extra context
        if "extra" in kwargs:
            for key, value in kwargs.pop("extra").items():
                scope.set_context(key, value)

        # Add remaining kwargs as extras
        for key, value in kwargs.items():
            scope.set_extra(key, value)

        # Capture exception
        sentry_sdk.capture_exception(exception)


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Manually capture a message and send to Sentry.

    Args:
        message: The message to capture
        level: Severity level (info, warning, error, fatal)
        **kwargs: Additional context
    """

    if not settings.SENTRY_DSN:
        logger.log(level, message, **kwargs)
        return

    with sentry_sdk.push_scope() as scope:
        # Add context similar to capture_exception
        if "tags" in kwargs:
            for key, value in kwargs.pop("tags").items():
                scope.set_tag(key, value)

        if "extra" in kwargs:
            for key, value in kwargs.pop("extra").items():
                scope.set_extra(key, value)

        sentry_sdk.capture_message(message, level=level)


def add_breadcrumb(
    message: str, category: str = "default", level: str = "info", **data
):
    """
    Add a breadcrumb to the current scope.
    Breadcrumbs are shown in Sentry along with the error for context.

    Args:
        message: Breadcrumb message
        category: Category (e.g., "auth", "db", "api")
        level: Severity level
        **data: Additional data
    """

    if not settings.SENTRY_DSN:
        return

    sentry_sdk.add_breadcrumb(
        category=category,
        message=message,
        level=level,
        data=data,
    )


def set_user_context(user_id: int, username: str = None, email: str = None, **kwargs):
    """
    Set user context for current scope.
    This will be included in all subsequent error reports.

    Args:
        user_id: User ID
        username: Username
        email: Email address
        **kwargs: Additional user attributes
    """

    if not settings.SENTRY_DSN:
        return

    user_data = {"id": user_id, "username": username, "email": email, **kwargs}

    # Remove None values
    user_data = {k: v for k, v in user_data.items() if v is not None}

    sentry_sdk.set_user(user_data)


def clear_user_context():
    """
    Clear user context (e.g., after logout).
    """

    if not settings.SENTRY_DSN:
        return

    sentry_sdk.set_user(None)


# Context manager for transactions
class SentryTransaction:
    """
    Context manager for Sentry transactions (performance monitoring).

    Usage:
        with SentryTransaction("process_checkout") as transaction:
            # do work
            transaction.set_tag("payment_method", "cash")
    """

    def __init__(self, name: str, op: str = "task"):
        self.name = name
        self.op = op
        self.transaction = None

    def __enter__(self):
        if settings.SENTRY_DSN:
            self.transaction = sentry_sdk.start_transaction(name=self.name, op=self.op)
            self.transaction.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            self.transaction.__exit__(exc_type, exc_val, exc_tb)

    def set_tag(self, key: str, value: str):
        """Set a tag on the transaction."""
        if self.transaction:
            self.transaction.set_tag(key, value)

    def set_data(self, key: str, value):
        """Set data on the transaction."""
        if self.transaction:
            self.transaction.set_data(key, value)
