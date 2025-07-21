import boto3
import pika
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
import uuid
import logging
from cachetools import cached, TTLCache

from shared.shared.database.database import get_db, engine
from shared.shared.models.models import ProcessingJob, Card, Base
from shared.config import settings
from . import schemas

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

cache = TTLCache(maxsize=100, ttl=300)

def get_s3_client():
    """
    Returns a boto3 S3 client.
    """
    if settings.TESTING:
        return boto3.client("s3", region_name="us-east-1")
    return boto3.client("s3", region_name=settings.S3_REGION)

from jose import JWTError, jwt

def get_user_id_from_token(authorization: str = Header(None)):
    """
    Validates the JWT token and returns the user ID.
    """
    if settings.TESTING and authorization:
        return 1

    if not authorization:
        logger.error("Authorization header missing")
        raise HTTPException(status_code=401, detail="Authorization header missing")

    token = authorization.split("Bearer ")[-1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            logger.error("Invalid token: 'sub' field missing")
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")


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
    logger.info(f"Creating job for user {user_id} with filename {job_request.filename}")
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

    try:
        # Generate a pre-signed URL for S3
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": object_key, "ContentType": job_request.contentType},
            ExpiresIn=3600,
        )
    except Exception as e:
        logger.error(f"Error generating pre-signed URL: {e}")
        raise HTTPException(status_code=500, detail="Could not generate upload URL")

    try:
        # Publish a message to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE)
        channel.basic_publish(
            exchange="",
            routing_key=settings.RABBITMQ_QUEUE,
            body=str(db_job.id),
        )
        connection.close()
    except Exception as e:
        logger.error(f"Error publishing message to RabbitMQ: {e}")
        # Rollback the database transaction
        db.delete(db_job)
        db.commit()
        raise HTTPException(status_code=500, detail="Could not create job")

    logger.info(f"Job {db_job.id} created successfully for user {user_id}")
    return {"jobId": db_job.id, "uploadUrl": presigned_url}

@app.get("/jobs/", response_model=List[schemas.ProcessingJob])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieves a list of processing jobs.
    """
    logger.info(f"Reading jobs with skip {skip} and limit {limit}")
    jobs = db.query(ProcessingJob).offset(skip).limit(limit).all()
    return jobs

@app.get("/api/v1/jobs/{job_id}", response_model=schemas.JobStatusResponse)
def read_job(job_id: int, db: Session = Depends(get_db), user_id: int = Depends(get_user_id_from_token)):
    """
    Retrieves the status of a specific processing job.
    """
    logger.info(f"Reading job {job_id} for user {user_id}")
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id, ProcessingJob.user_id == user_id).first()
    if db_job is None:
        logger.error(f"Job {job_id} not found for user {user_id}")
        raise HTTPException(status_code=404, detail="Job not found")

    results = None
    if db_job.status == "COMPLETED":
        results = db_job.cards

    return {"status": db_job.status, "results": results}

@app.put("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def update_job(job_id: int, job: schemas.ProcessingJobCreate, db: Session = Depends(get_db)):
    """
    Updates a processing job.
    """
    logger.info(f"Updating job {job_id}")
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        logger.error(f"Job {job_id} not found for update")
        raise HTTPException(status_code=404, detail="Job not found")
    for var, value in vars(job).items():
        setattr(db_job, var, value) if value else None
    db.commit()
    db.refresh(db_job)
    logger.info(f"Job {job_id} updated successfully")
    return db_job

@app.delete("/jobs/{job_id}", response_model=schemas.ProcessingJob)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    """
    Deletes a processing job.
    """
    logger.info(f"Deleting job {job_id}")
    db_job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if db_job is None:
        logger.error(f"Job {job_id} not found for deletion")
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(db_job)
    db.commit()
    logger.info(f"Job {job_id} deleted successfully")
    return db_job

@app.get("/api/v1/collections", response_model=List[schemas.Card])
@cached(cache)
def get_collection(db: Session = Depends(get_db), user_id: int = Depends(get_user_id_from_token)):
    """
    Retrieves all cards for the authenticated user.
    """
    logger.info(f"Retrieving collection for user {user_id}")
    cards = (
        db.query(Card)
        .join(ProcessingJob)
        .filter(ProcessingJob.user_id == user_id)
        .all()
    )
    logger.info(f"Found {len(cards)} cards for user {user_id}")
    return cards
