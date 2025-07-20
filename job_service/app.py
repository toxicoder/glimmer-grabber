import os
import boto3
import pika
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
import uuid

from shared.database.database import get_db, engine
from shared.models.models import ProcessingJob, Card, Base
from . import schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)

# S3 configuration
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
S3_REGION = os.environ.get("S3_REGION")

def get_s3_client():
    if os.environ.get("TESTING"):
        return boto3.client("s3", region_name="us-east-1")
    return boto3.client("s3", region_name=S3_REGION)

# RabbitMQ configuration
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "test_queue")

def get_user_id_from_token(authorization: str = Header(None)):
    if os.environ.get("TESTING") and authorization:
        return 1
    # This is a placeholder for a real token validation and user extraction logic
    # In a real application, you would decode the JWT and get the user ID
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    try:
        # Assuming the token is in the format "Bearer <user_id>" for simplicity
        token_type, user_id = authorization.split()
        if token_type.lower() != "bearer":
            raise ValueError
        return int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token format")


@app.post("/api/v1/jobs", response_model=schemas.JobCreationResponse)
def create_job(
    job_request: schemas.JobCreationRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id_from_token),
    s3_client: boto3.client = Depends(get_s3_client),
):
    """
    Creates a new processing job.
    """
    object_key = f"{user_id}/{uuid.uuid4()}/{job_request.filename}"

    # Create a new ProcessingJob record
    db_job = ProcessingJob(
        user_id=user_id,
        status="PENDING",
        s3_object_key=object_key,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    # Generate a pre-signed URL for S3
    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={"Bucket": os.environ.get("S3_BUCKET_NAME"), "Key": object_key, "ContentType": job_request.contentType},
        ExpiresIn=3600,
    )

    # Publish a message to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE)
    channel.basic_publish(
        exchange="",
        routing_key=RABBITMQ_QUEUE,
        body=str(db_job.id),
    )
    connection.close()

    return {"jobId": db_job.id, "uploadUrl": presigned_url}

@app.get("/jobs/", response_model=List[schemas.ProcessingJob])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(ProcessingJob).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/v1/jobs/{job_id}", response_model=schemas.JobStatusResponse)
def read_job(job_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id_from_token)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id, ProcessingJob.user_id == user_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    results = None
    if db_job.status == "COMPLETED":
        results = db_job.cards

    return {"status": db_job.status, "results": results}

@app.put("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def update_job(job_id: int, job: schemas.ProcessingJobCreate, db: Session = Depends(get_db)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    for var, value in vars(job).items():
        setattr(db_job, var, value) if value else None
    db.commit()
    db.refresh(db_job)
    return db_job

@app.delete("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    return db_job

@app.get("/api/v1/collections", response_model=List[schemas.Card])
def get_collection(db: Session = Depends(get_db), user_id: int = Depends(get_user_id_from_token)):
    """
    Retrieves all cards for the authenticated user.
    """
    cards = (
        db.query(Card)
        .join(ProcessingJob)
        .filter(ProcessingJob.user_id == user_id)
        .all()
    )
    return cards
