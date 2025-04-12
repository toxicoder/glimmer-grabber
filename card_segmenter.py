import cv2
import numpy as np
from typing import List, Dict, Any

class CardSegmenter:
    """
    Segments cards from an image using a YOLOv8 segmentation model.
    """
    def __init__(self, model_path: str = "yolov8n-seg.pt") -> None:
        """Initializes the CardSegmenter with a YOLOv8-seg model.

        Args:
            model_path (str): Path to the YOLOv8-seg model file (default: yolov8n-seg.pt).

        Raises:
            ImportError: If the 'ultralytics' package is not installed.
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except ImportError:
            raise ImportError("Please install the 'ultralytics' package to use YOLOv8.")

    def segment_cards(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detects and segments cards in an image.

        Args:
            image (np.ndarray): The input image as a NumPy array.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents a card segmentation and contains:
                - "mask" (np.ndarray): A binary mask representing the card segmentation.
                - "bbox" (List[float]): A bounding box in the format [x1, y1, x2, y2].
            Returns an empty list if no cards are detected.

        Raises:
            Exception: If an error occurs during segmentation.
        """
        try:
            results = self.model.predict(image)
            if results:
                masks = results[0].masks.data.cpu().numpy()
                boxes = results[0].boxes.xyxy.cpu().numpy()
                segmentations: List[Dict[str, Any]] = []
                for i in range(len(masks)):
                    mask = masks[i]
                    bbox = boxes[i]
                    segmentations.append({"mask": mask, "bbox": bbox})
                return segmentations
            else:
                return []
        except Exception as e:
            print(f"Error during segmentation: {e}")
            return []
