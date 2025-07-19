# Dockerfile for processing_service
FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# Command to run the Celery worker
CMD ["celery", "-A", "celery_app", "worker", "-l", "info"]
