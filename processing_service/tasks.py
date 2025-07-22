import hashlib
from botocore.exceptions import ClientError
from sqlalchemy.exc import SQLAlchemyError
from .celery_app import celery_app
from .core.image_processing import process_image
from .core.data_extraction import extract_data
from .utils.logging_utils import setup_logging
from .utils.file_utils import download_image_from_s3, is_image_processed
from .database import get_db, ProcessingJob, Card
from shared.shared.models.models import ProcessedImage

logger = setup_logging()

class ImageProcessingError(Exception):
    pass

class DataExtractionError(Exception):
    pass

@celery_app.task(autoretry_for=(Exception,), max_retries=3, default_retry_delay=60)
def process_image_task(jobId: int, image_key: str) -> None:
    """
    Celery task to process an image and extract data.
    """
    logger.info(f"Processing job {jobId} with image {image_key}")

    db = next(get_db())
    job = db.query(ProcessingJob).filter(ProcessingJob.id == jobId).first()

    if not job:
        logger.error(f"Job {jobId} not found in the database.")
        return

    job.status = "RUNNING"
    db.commit()

    try:
        try:
            image_bytes = download_image_from_s3(image_key)
        except ClientError as e:
            raise ImageProcessingError(f"Error downloading image from S3: {e}")

        if is_image_processed(image_bytes, db):
            logger.info(f"Image in job {jobId} has already been processed. Skipping.")
            job.status = "COMPLETED"
            db.commit()
            return

        try:
            processed_data = process_image(image_bytes)
        except Exception as e:
            raise ImageProcessingError(f"Error processing image: {e}")

        try:
            card_details = extract_data(processed_data)
        except Exception as e:
            raise DataExtractionError(f"Error extracting data: {e}")

        for card_data in card_details:
            card = Card(job_id=jobId, content=str(card_data))
            db.add(card)

        image_hash = hashlib.sha256(image_bytes).hexdigest()
        processed_image = ProcessedImage(hash=image_hash)
        db.add(processed_image)

        job.status = "COMPLETED"
        db.commit()
        logger.info(f"Job {jobId} completed successfully.")

    except (ImageProcessingError, DataExtractionError, SQLAlchemyError) as e:
        job.status = "FAILED"
        job.error_message = str(e)
        db.commit()
        logger.error(f"Job {jobId} failed: {e}")
        raise
