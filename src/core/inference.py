# Standard library imports
import logging
from typing import Any, Dict, List

# Third-party imports
import numpy as np

# Application-specific imports
from src.core.card_segmenter import CardSegmenter # For segmenting cards from images
# Assuming ImageProcessingError might be relevant, though not explicitly raised here,
# it's good practice if other core functions use it.
# from src.core.exceptions import ImageProcessingError

# Module-level logger
logger = logging.getLogger(__name__)

# run_inference now directly uses the confidence score from the segmenter's results.
# The confidence_threshold is passed to it.
def run_inference(
    image: np.ndarray,
    segmenter: CardSegmenter,
    confidence_threshold: float, # No default here, should be provided by caller
    original_image_path: str    # Added to pass to segment_cards
) -> List[Dict[str, Any]]:
    """
    Runs card segmentation inference on a preprocessed image using a CardSegmenter
    and filters results based on a confidence threshold.

    Args:
        image (np.ndarray): The preprocessed image.
        segmenter (CardSegmenter): An initialized CardSegmenter instance.
        confidence_threshold (float): Minimum confidence score for a detection to be included.
        original_image_path (str): Path of the original image, for naming saved segments.


    Returns:
        List[Dict[str, Any]]: Filtered list of detected card segmentations.
                              Each dict includes 'confidence' if provided by segmenter.
    Raises:
        RuntimeError: Propagated from `CardSegmenter`.
    """
    logger.info(f"Running inference on image (shape: {image.shape}, original_path: {original_image_path}) with confidence_threshold: {confidence_threshold}")
    try:
        # CardSegmenter.segment_cards now requires original_image_path
        segmentation_results: List[Dict[str, Any]] = segmenter.segment_cards(image, original_image_path)

        if not segmentation_results:
            logger.info(f"Segmentation returned no results for {original_image_path}.")
            return []

        # Filter based on confidence. Assumes 'confidence' key is in each result dict.
        # If 'confidence' might be missing, .get('confidence', 0.0) is safer.
        # YOLOv8 results usually include a 'conf' tensor, which CardSegmenter should map to 'confidence'.
        filtered_results = [
            result for result in segmentation_results
            if result.get("confidence", 0.0) >= confidence_threshold
        ]

        num_total = len(segmentation_results)
        num_filtered = len(filtered_results)
        logger.info(f"Segmentation found {num_total} instances. After confidence filtering ({confidence_threshold}), {num_filtered} instances remain.")

        return filtered_results

    except RuntimeError as e:
        logger.error(f"A runtime error occurred during inference via CardSegmenter: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.exception(f"An unexpected error occurred during the inference process: {e}")
        return []
