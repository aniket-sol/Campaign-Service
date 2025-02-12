from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Create a Celery instance
app = Celery('Campaign_Service',
             broker=CELERY_BROKER_URL,
             include=['tasks'])

app.conf.update(
    result_backend=CELERY_RESULT_BACKEND,  # Use environment variable for result backend
    task_serializer='json',  # Data serialization method
    result_serializer='json',
    accept_content=['json'],  # Only accept JSON content
    timezone='Asia/Kolkata',
    enable_utc=False,  # Disable UTC
)