import cv2
import numpy as np
from typing import List, Dict, Any

class CardSegmenter:
    def __init__(self, model_path: str = "yolov8n-seg.pt") -> None:
        """Initializes the CardSegmenter with a YOLOv8-seg model.

        Args:
            model_path (str): Path to the YOLOv8-seg model file (default: yolov8n-seg.pt).
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except ImportError:
            raise ImportError("Please install the 'ultralytics' package to use YOLOv8.")

    def segment_cards(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detects and segments cards in an image.

        Args:
            image (NumPy array): The input image.

        Returns:
            list: A list of dictionaries, where each dictionary contains:
                  - "mask": A binary mask (NumPy array) representing the card segmentation.
                  - "bbox": A bounding box (list of 4 floats) in the format [x1, y1, x2, y2].
                  Returns an empty list if no cards are detected or an error occurs.
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
