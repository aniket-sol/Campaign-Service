from celery import Celery

# Create a Celery instance
app = Celery('Campaign_Service', broker='redis://localhost:6379/0',include=['tasks'])

app.conf.update(
    result_backend='redis://localhost:6379/0',  # This stores task results in Redis
    task_serializer='json',  # Data serialization method
    result_serializer='json',
    accept_content=['json'],  # Only accept JSON content
    timezone='Asia/Kolkata',
    enable_utc=False,  # Disable UTC
)

