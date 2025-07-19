from .celery_app import celery_app
from .core.image_processing import process_image
from .core.data_extraction import extract_data
from .utils.logging_utils import setup_logging

logger = setup_logging()

@celery_app.task
def process_image_task(image_bytes):
    """
    Celery task to process an image and extract data.
    """
    logger.info("Processing image...")
    processed_data = process_image(image_bytes)
    logger.info(f"Processed data: {processed_data}")

    logger.info("Extracting data...")
    extracted_data = extract_data(processed_data)
    logger.info(f"Extracted data: {extracted_data}")

    return extracted_data
