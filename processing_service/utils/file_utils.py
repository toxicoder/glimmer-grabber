import os
import boto3
import requests

S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

def download_image_from_s3(image_key: str) -> bytes:
    """
    Downloads an image from S3 and returns its content as bytes.
    """
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
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
