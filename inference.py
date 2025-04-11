from card_segmenter import CardSegmenter

def run_inference(image, segmenter, confidence_threshold=0.5):
    """Runs inference on a preprocessed image using the CardSegmenter.

    Args:
        image (NumPy array): The preprocessed image.
        segmenter (CardSegmenter): An instance of the CardSegmenter class.
        confidence_threshold (float): Minimum confidence score for detections.

    Returns:
        list: A list of dictionaries, where each dictionary contains:
              - "mask": A binary mask (NumPy array) representing the card segmentation.
              - "bbox": A bounding box (list of 4 floats) in the format [x1, y1, x2, y2].
              Returns an empty list if no cards are detected or an error occurs.
    """
    try:
        results = segmenter.segment_cards(image)
        filtered_results = []
        for result in results:
            # Assuming segment_cards now returns confidence scores as well
            if "confidence" in result and result["confidence"] >= confidence_threshold:
                filtered_results.append(result)
        return filtered_results
    except Exception as e:
        print(f"Error during inference: {e}")
        return []
