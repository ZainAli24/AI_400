"""
Celery tasks - Optional
To use Celery:
1. Install: pip install celery redis
2. Start Redis: docker run -d -p 6379:6379 redis
3. Start Celery worker: celery -A app.tasks.celery_tasks worker --loglevel=info
"""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)


@celery_app.task
def send_email_celery(email: str, message: str):
    """Send email using Celery"""
    import time
    print(f"Sending email to {email}")
    time.sleep(2)
    print(f"Email sent to {email}")
    return {"status": "sent", "email": email}


@celery_app.task
def process_data_celery(data: dict):
    """Process data using Celery"""
    import time
    print(f"Processing data: {data}")
    time.sleep(3)
    print("Data processing complete")
    return {"status": "processed", "data": data}
