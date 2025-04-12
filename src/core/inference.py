from .card_segmenter import CardSegmenter
import numpy as np
from typing import List, Dict, Any

def run_inference(image: np.ndarray, segmenter: CardSegmenter) -> List[Dict[str, Any]]:
    """Runs inference on a preprocessed image using the CardSegmenter.

    Args:
        image: The preprocessed image as a NumPy array.
        segmenter: An instance of the CardSegmenter class.

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
        return segmenter.segment_cards(image)
    except Exception as e:
        print(f"Error during inference: {e}")
        return []
