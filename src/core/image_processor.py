import cv2
import os
from typing import List, Optional

from src.core.card_segmenter import CardSegmenter  # Import here to avoid circular import

def process_images(image_files: List[str], output_path: str, save_segmented_images: bool, save_segmented_images_path: str) -> None:
    """Processes a list of image files to segment cards.

    The function reads each image, performs card segmentation using the CardSegmenter,
    and handles any errors that occur during processing.

    Args:
        image_files: A list of paths to the image files.
        output_path: The base directory where processed images or data might be saved (not currently used in this function, but kept for potential future use).
        save_segmented_images: A boolean indicating whether to save segmented card images (not currently used in this function, but handled within the CardSegmenter).
        save_segmented_images_path: The path to save segmented card images if enabled (not currently used in this function, but handled within the CardSegmenter).

    Processing Steps for Each Image:
    1. Read the image from the given path using OpenCV (cv2.imread).
    2. Check if the image was successfully read. If not (image is None), print an error message and skip to the next image.
    3. If the image was read successfully, perform card segmentation using the CardSegmenter's segment_cards method.
    4. Append the processed image path to a log file ("data/processed_images.log") to keep track of processed images.
    5. Handle any exceptions that might occur during image reading or segmentation, printing an error message with the image path and exception details.
    """
    card_segmenter: CardSegmenter = CardSegmenter()

    with open(os.path.join("data", "processed_images.log"), "a") as f:
        for image_path in image_files:
            print(f"Processing image: {image_path}")
            try:
                # Read the image using cv2
                image: Optional[cv2.Mat] = cv2.imread(image_path)
                if image is None:
                    if not os.path.exists(image_path):
                        print(f"Error: Could not read image at {image_path}: File not found.")
                    else:
                        print(f"Error: Could not read image at {image_path}: Unsupported format or corrupted file.")
                    continue

                # Perform card segmentation
                segmentations = card_segmenter.segment_cards(image)

                f.write(image_path + "\n")
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
