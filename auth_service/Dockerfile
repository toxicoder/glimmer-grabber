# Placeholder Dockerfile for auth_service
FROM python:3.9-slim

WORKDIR /app

COPY ./auth_service .

# Install the shared module
COPY ./shared /tmp/shared
RUN pip install /tmp/shared

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
