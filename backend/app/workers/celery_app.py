"""
NeuroCron Celery Application
Background task processing for AutoCron and other async operations
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "neurocron",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.autocron_tasks",
        "app.workers.trend_tasks",
        "app.workers.content_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
)

# Periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    # AutoCron: Check and execute scheduled tasks every minute
    "autocron-execute-scheduled": {
        "task": "app.workers.autocron_tasks.execute_scheduled_tasks",
        "schedule": 60.0,  # Every minute
    },
    
    # AutoCron: Optimize campaigns hourly
    "autocron-optimize-campaigns": {
        "task": "app.workers.autocron_tasks.optimize_campaigns",
        "schedule": crontab(minute=0),  # Every hour
    },
    
    # TrendRadar: Check trends every 15 minutes
    "trendradar-check-trends": {
        "task": "app.workers.trend_tasks.check_trends",
        "schedule": 900.0,  # Every 15 minutes
    },
    
    # CrisisShield: Monitor brand mentions every 5 minutes
    "crisisshield-monitor-brand": {
        "task": "app.workers.trend_tasks.monitor_brand_mentions",
        "schedule": 300.0,  # Every 5 minutes
    },
    
    # Analytics: Sync platform metrics every 30 minutes
    "analytics-sync-metrics": {
        "task": "app.workers.autocron_tasks.sync_platform_metrics",
        "schedule": 1800.0,  # Every 30 minutes
    },
    
    # Reports: Generate daily reports at 6 AM UTC
    "reports-daily-summary": {
        "task": "app.workers.autocron_tasks.generate_daily_reports",
        "schedule": crontab(hour=6, minute=0),
    },
    
    # Cleanup: Archive old data weekly
    "cleanup-archive-old-data": {
        "task": "app.workers.autocron_tasks.archive_old_data",
        "schedule": crontab(day_of_week=0, hour=3, minute=0),  # Sunday 3 AM
    },
    
    # OAuth: Refresh tokens every 15 minutes
    "oauth-refresh-tokens": {
        "task": "app.workers.autocron_tasks.refresh_oauth_tokens",
        "schedule": 900.0,  # Every 15 minutes
    },
    
    # OAuth: Cleanup expired states hourly
    "oauth-cleanup-states": {
        "task": "app.workers.autocron_tasks.cleanup_expired_oauth_states",
        "schedule": crontab(minute=30),  # Every hour at :30
    },
}

