from core.image_processing import process_image
from core.data_extraction import extract_data
from utils.logging_utils import setup_logging
from PIL import Image
import io

def create_dummy_image() -> bytes:
    """Creates a dummy 10x10 black image."""
    img = Image.new('RGB', (10, 10), color = 'black')
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()

def main():
    """
    Main function to demonstrate the use of the refactored functions.
    """
    logger = setup_logging()

    # Example usage:
    # 1. Create a dummy image
    logger.info("Creating a dummy image.")
    image_bytes = create_dummy_image()

    if image_bytes:
        # 2. Process the image
        logger.info("Processing image...")
        processed_data = process_image(image_bytes)
        logger.info(f"Processed data: {processed_data}")

        # 3. Extract data from the processed data
        logger.info("Extracting data...")
        extracted_data = extract_data(processed_data)
        logger.info(f"Extracted data: {extracted_data}")
    else:
        logger.error("Failed to create dummy image.")

if __name__ == "__main__":
    main()
