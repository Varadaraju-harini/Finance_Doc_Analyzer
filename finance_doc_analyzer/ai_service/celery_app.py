from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "celery_tasks"  # This should be the module where your Celery tasks are defined
    ]
)

# Optional Celery config
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    worker_prefetch_multiplier=1,  # better for parallel large tasks
    task_acks_late=True
)

if __name__ == "__main__":
    celery_app.start()
