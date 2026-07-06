from celery import Celery

from core.config import settings

celery_app = Celery(
    "revenue_leakage_radar",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["workers.tasks.ingestion", "workers.tasks.verification"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=True,
    worker_concurrency=settings.celery_worker_concurrency,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
)
