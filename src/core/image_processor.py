import cv2
import os
from typing import List, Optional, Dict

from src.core.card_segmenter import CardSegmenter

def process_images(image_files: List[str], output_path: str, save_segmented_images: bool, save_segmented_images_path: str) -> List[Dict]:
    """Processes a list of image files to segment cards and returns processed data.

    The function reads each image, performs card segmentation using the CardSegmenter,
    and handles any errors that occur during processing.  It returns a list of dictionaries,
    where each dictionary contains the image path and segmentation data.

    Args:
        image_files: A list of paths to the image files.
        output_path: The base directory where processed images or data might be saved.
        save_segmented_images: A boolean indicating whether to save segmented card images.
        save_segmented_images_path: The path to save segmented card images if enabled.

    Returns:
        A list of dictionaries, where each dictionary contains:
            - "image_path": The path to the processed image.
            - "segmentations": The segmentation data returned by the CardSegmenter.
              If segmentation fails or the image cannot be read, "segmentations" will be None.

    Processing Steps for Each Image:
    1. Read the image from the given path using OpenCV (cv2.imread).
    2. Check if the image was successfully read. If not (image is None), print an error message and skip to the next image.
    3. If the image was read successfully, perform card segmentation using the CardSegmenter's segment_cards method.
    4. Store the image path and segmentation data (or None if failed) in a dictionary.
    5. Append the dictionary to the list of processed images.
    6. Handle any exceptions that might occur during image reading or segmentation, printing an error message.
    """
    card_segmenter: CardSegmenter = CardSegmenter()
    processed_data: List[Dict] = []

    for image_path in image_files:
        print(f"Processing image: {image_path}")
        try:
            image: Optional[cv2.Mat] = cv2.imread(image_path)
            if image is None:
                if not os.path.exists(image_path):
                    print(f"Error: Could not read image at {image_path}: File not found.")
                else:
                    print(f"Error: Could not read image at {image_path}: Unsupported format or corrupted file.")
                processed_data.append({"image_path": image_path, "segmentations": None})
                continue

            segmentations = card_segmenter.segment_cards(image)
            processed_data.append({"image_path": image_path, "segmentations": segmentations})

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            processed_data.append({"image_path": image_path, "segmentations": None})

    return processed_data
