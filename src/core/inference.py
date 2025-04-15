import numpy as np
from typing import List, Dict, Any
import logging
from src.core.card_segmenter import CardSegmenter
"""Runs inference on preprocessed images."""

logger = logging.getLogger(__name__)

def run_inference(image: np.ndarray, segmenter: CardSegmenter, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Runs inference on a preprocessed image using the CardSegmenter.

    This function takes a preprocessed image and a CardSegmenter instance to detect
    and segment cards within the image. It returns a list of dictionaries, each
    representing a detected card with its segmentation details.

    Args:
        image: The preprocessed image as a NumPy array.
        segmenter: An instance of the CardSegmenter class, used for card detection
            and segmentation.

    Returns:
        A list of dictionaries, where each dictionary represents a detected card and contains:
            - "mask": A binary mask representing the card segmentation.
            - "bbox": A bounding box in the format [x1, y1, x2, y2].
            - "image": The segmented card image.
            - "card_name": The identified card name.
        Returns an empty list if no cards are detected or if an error occurs.

    Raises:
        Exception: If an error occurs during inference.
    """
    try:
        results = segmenter.segment_cards(image)
        if not results:
            return []
        # Filter results by confidence threshold, assuming 'confidence' is in the result
        filtered_results = [result for result in results if result.get("confidence", 0) >= confidence_threshold]
        return filtered_results
    except Exception as e:
        logger.exception(f"Error during inference: {e}")
        return [{"error": f"Inference failed: {e}"}]
