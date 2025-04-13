import cv2
import os
from typing import List, Optional

from src.core.card_segmenter import CardSegmenter  # Import here to avoid circular import

def process_images(image_files: List[str], output_path: str, save_segmented_images: bool, save_segmented_images_path: str) -> None:
    card_segmenter: CardSegmenter = CardSegmenter()

    with open(os.path.join("data", "processed_images.log"), "a") as f:
        for image_path in image_files:
            #if image_path in processed_images:  # This will be handled in cli.py
            #    print(f"Skipping already processed image: {image_path}")
            #    continue

            print(f"Processing image: {image_path}")
            try:
                # Read the image using cv2
                image: Optional[cv2.Mat] = cv2.imread(image_path)
                if image is None:
                    print(f"Error: Could not read image at {image_path}")
                    continue

                # Perform card segmentation
                segmentations = card_segmenter.segment_cards(image)

                f.write(image_path + "\n")
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
