# Placeholder Dockerfile for job_service
FROM python:3.9-slim

WORKDIR /app

COPY job_service/requirements.txt .

RUN pip install -r requirements.txt

COPY job_service/ .

# Install the shared module
COPY shared /tmp/shared
RUN pip install /tmp/shared

CMD ["python", "app.py"]
