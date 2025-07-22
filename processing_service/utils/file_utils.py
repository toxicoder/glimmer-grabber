import boto3
import requests
import hashlib
from shared.shared.models.models import ProcessedImage
from shared.config import get_settings

settings = get_settings()

def download_image_from_s3(image_key: str) -> bytes:
    """
    Downloads an image from S3 and returns its content as bytes.
    """
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name=settings.S3_REGION,
    )
    try:
        response = s3.get_object(Bucket=settings.S3_BUCKET_NAME, Key=image_key)
        return response["Body"].read()
    except Exception as e:
        print(f"Error downloading image from S3: {e}")
        return b""

def download_image(url: str) -> bytes:
    """
    Downloads an image from a URL and returns its content as bytes.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")
        return b""

from sqlalchemy.orm import Session

def is_image_processed(image_bytes: bytes, db: Session) -> bool:
    """
    Checks if an image has been processed before based on its hash.
    """
    image_hash = hashlib.sha256(image_bytes).hexdigest()
    processed_image = db.query(ProcessedImage).filter(ProcessedImage.hash == image_hash).first()
    return processed_image is not None
