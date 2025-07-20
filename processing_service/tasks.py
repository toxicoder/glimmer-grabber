from .celery_app import celery_app
from .core.image_processing import process_image
from .core.data_extraction import extract_data
from .utils.logging_utils import setup_logging
from .utils.file_utils import download_image_from_s3
from .database import get_db, ProcessingJob, Card

logger = setup_logging()

@celery_app.task
def process_image_task(jobId, image_key):
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
        image_bytes = download_image_from_s3(image_key)
        # Replace with actual image processing logic
        processed_data = process_image(image_bytes)
        # Replace with actual data extraction logic
        extracted_data = extract_data(processed_data)

        card_details = extract_data(processed_data)

        for card_data in card_details:
            card = Card(job_id=jobId, content=str(card_data))
            db.add(card)

        job.status = "COMPLETED"
        db.commit()
        logger.info(f"Job {jobId} completed successfully.")
    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        db.commit()
        logger.error(f"Job {jobId} failed: {e}")
