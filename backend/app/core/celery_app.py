"""
Celery configuration for background tasks
Handles async operations like TSE signing, webhook processing, exports, etc.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "stumpfworks_pos",
    broker=str(settings.REDIS_URL) if settings.REDIS_URL else "redis://redis:6379/0",
    backend=str(settings.REDIS_URL) if settings.REDIS_URL else "redis://redis:6379/0",
    include=[
        "app.services.tse.tasks",
        "app.services.payment.tasks",
        "app.services.export.tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Berlin",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
)

# Periodic tasks configuration (Celery Beat)
celery_app.conf.beat_schedule = {
    "sync-pending-tse-signatures": {
        "task": "app.services.tse.tasks.sync_pending_signatures",
        "schedule": 60.0,  # Every minute
    },
    "cleanup-old-exports": {
        "task": "app.services.export.tasks.cleanup_old_exports",
        "schedule": 86400.0,  # Once per day
    },
    "health-check-integrations": {
        "task": "app.services.health.tasks.check_integrations",
        "schedule": 300.0,  # Every 5 minutes
    },
}


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup."""
    return f"Request: {self.request!r}"
