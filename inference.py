from card_segmenter import CardSegmenter
import numpy as np
from typing import List, Dict, Any

def run_inference(image: np.ndarray, segmenter: CardSegmenter, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Runs inference on a preprocessed image using the CardSegmenter.

    Args:
        image (np.ndarray): The preprocessed image as a NumPy array.
        segmenter (CardSegmenter): An instance of the CardSegmenter class.
        confidence_threshold (float): Minimum confidence score for detections (default: 0.5).

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a detected card and contains:
            - "mask" (np.ndarray): A binary mask representing the card segmentation.
            - "bbox" (List[float]): A bounding box in the format [x1, y1, x2, y2].
        Returns an empty list if no cards are detected or if an error occurs.

    Raises:
        Exception: If an error occurs during inference.
    """
    try:
        results = segmenter.segment_cards(image)
        filtered_results: List[Dict[str, Any]] = []
        for result in results:
            # Assuming segment_cards now returns confidence scores as well
            if "confidence" in result and result["confidence"] >= confidence_threshold:
                filtered_results.append(result)
        return filtered_results
    except Exception as e:
        print(f"Error during inference: {e}")
        return []
