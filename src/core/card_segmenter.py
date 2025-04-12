import cv2
import numpy as np
from typing import List, Dict, Any
from .config_manager import ConfigManager
import pytesseract

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
                - "image" (np.ndarray, optional): The segmented card image if keep_split_card_images is True.
            Returns an empty list if no cards are detected.

        Raises:
            Exception: If an error occurs during segmentation.
        """
        config_manager = ConfigManager()
        keep_split_card_images = config_manager.get_keep_split_card_images()
        try:
            results = self.model.predict(image)
            if results:
                masks = results[0].masks.data.cpu().numpy()
                boxes = results[0].boxes.xyxy.cpu().numpy()
                segmentations: List[Dict[str, Any]] = []
                for i in range(len(masks)):
                    mask = masks[i]
                    bbox = boxes[i]
                    segmentation: Dict[str, Any] = {"mask": mask, "bbox": bbox}
                    x1, y1, x2, y2 = map(int, bbox)
                    segmented_image = image[y1:y2, x1:x2]
                    segmentation["image"] = segmented_image
                    card_name = self.identify_card_name(segmented_image)
                    segmentation["card_name"] = card_name
                    segmentations.append(segmentation)
                config_manager = ConfigManager()
                if config_manager.get_save_segmented_images():
                    output_dir = config_manager.get_save_segmented_images_path()
                    if output_dir:
                        self.save_segmented_cards(segmentations, output_dir)
                return segmentations
            else:
                return []
        except Exception as e:
            print(f"Error during segmentation: {e}")
            return []

    def identify_card_name(self, image: np.ndarray) -> str:
        """Identifies the card name from an image using OCR.

        Args:
            image (np.ndarray): The segmented card image.

        Returns:
            str: The identified card name, or "Unknown Card" if identification fails.
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Adding some preprocessing to improve OCR accuracy
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            text = pytesseract.image_to_string(thresh).strip()
            if text:
                return text
            else:
                return "Unknown Card"
        except Exception as e:
            print(f"Error during card name identification: {e}")
            return "Unknown Card"

    def save_segmented_cards(self, segmentations: List[Dict[str, Any]], output_dir: str) -> None:
        """Saves the segmented card images to the specified directory.

        Args:
            segmentations (List[Dict[str, Any]]): A list of card segmentation dictionaries.
            output_dir (str): The directory to save the segmented card images.
        """
        import os
        import re

        def sanitize_filename(filename: str) -> str:
            """Sanitizes a string to be safe for use as a filename.

            Replaces any character that is not alphanumeric, underscore, or dot with an underscore.
            """
            return re.sub(r"[^a-zA-Z0-9_.]", "_", filename)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, segmentation in enumerate(segmentations):
            image = segmentation["image"]
            card_name = segmentation.get("card_name", "Unknown Card")
            if card_name and card_name != "Unknown Card":
                filename = os.path.join(output_dir, f"{sanitize_filename(card_name)}.png")
            else:
                filename = os.path.join(output_dir, f"card_{i}.png")
            cv2.imwrite(filename, image)
