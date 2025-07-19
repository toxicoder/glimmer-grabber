from celery import Celery

# Create a Celery instance
celery_app = Celery(
    'processing_service',
    broker='amqp://guest:guest@rabbitmq:5672//',
    backend='rpc://',
    include=['tasks']
)

# Optional: Configure Celery further if needed
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],  # Ensure Celery accepts JSON content
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()
