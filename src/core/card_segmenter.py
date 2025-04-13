import cv2
import numpy as np
from typing import List, Dict, Any, Optional
from .config_manager import ConfigManager
import pytesseract
import os
import re
import logging

class CardSegmenter:
    """Segments cards from an image using a YOLOv8 segmentation model.

    Card Segmentation Process:
    1. The input image is passed to the YOLOv8 model for object detection and segmentation.
    2. YOLOv8 identifies potential card instances and provides segmentation masks and bounding boxes.
    3. For each detected instance, a binary mask is created to isolate the card from the background.
    4. The bounding box is used to crop the card image from the original image.
    5. The cropped image is then passed to the card name identification module.

    YOLO Model:
    - The `CardSegmenter` uses a YOLOv8 segmentation model (`yolov8n-seg.pt` by default).
    - YOLO (You Only Look Once) is a real-time object detection system that divides an image into a grid and predicts bounding boxes and class probabilities for each grid cell.
    - The 'segmentation' version (YOLOv8-seg) extends this by also predicting a segmentation mask for each detected object, allowing for pixel-level separation of objects from the background.
    """

    def __init__(self, model_path: str = "yolov8n-seg.pt", config_manager: Optional[ConfigManager] = None) -> None:
        """Initializes the CardSegmenter with a YOLOv8-seg model.

        Args:
            model_path: Path to the YOLOv8-seg model file (default: "yolov8n-seg.pt").
            config_manager: An optional ConfigManager instance. If None, a default ConfigManager will be created.
        """
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
        except ImportError:
            raise ImportError("Please install the 'ultralytics' package to use YOLOv8.")

        if config_manager is None:
            self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager

        self.logger = logging.getLogger(__name__)

    def segment_cards(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detects and segments cards in an image.

        Args:
            image: The input image as a NumPy array.

        Returns:
            A list of dictionaries, where each dictionary represents a card segmentation and contains:
                - "mask": A binary mask representing the card segmentation.
                - "bbox": A bounding box in the format [x1, y1, x2, y2].
                - "image": The segmented card image.
                - "card_name": The identified card name.
            Returns an empty list if no cards are detected.

        Raises:
            Exception: If an error occurs during segmentation.
        """
        keep_split_card_images: bool = self.config_manager.get_keep_split_card_images()
        try:
            results = self.model.predict(image)
            if results:
                masks: np.ndarray = results[0].masks.data.cpu().numpy()
                boxes: np.ndarray = results[0].boxes.xyxy.cpu().numpy()
                segmentations: List[Dict[str, Any]] = []
                for i in range(len(masks)):
                    mask: np.ndarray = masks[i]
                    bbox: np.ndarray = boxes[i]
                    segmentation: Dict[str, Any] = {"mask": mask, "bbox": bbox}
                    x1, y1, x2, y2 = map(int, bbox)
                    segmented_image: np.ndarray = image[y1:y2, x1:x2]
                    segmentation["image"] = segmented_image
                    card_name: str = self.identify_card_name(segmented_image)
                    segmentation["card_name"] = card_name
                    segmentations.append(segmentation)
                if self.config_manager.get_save_segmented_images():
                    output_dir: Optional[str] = self.config_manager.get_save_segmented_images_path()
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

        Card Name Identification Logic:
        1. The segmented card image is converted to grayscale.
        2. Apply CLAHE for contrast enhancement.
        3. Apply median blur for noise reduction.
        4. Apply adaptive thresholding to handle varying lighting conditions.
        5. Tesseract OCR is used to extract text from the preprocessed image.
        6. The extracted text is stripped of leading/trailing whitespace.
        7. If text is extracted, it is returned as the card name; otherwise, "Unknown Card" is returned.

        Args:
            image: The segmented card image.

        Returns:
            The identified card name, or "Unknown Card" if identification fails.
        """
        try:
            gray: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Apply CLAHE for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            cl1 = clahe.apply(gray)
            # Apply median blur for noise reduction
            blurred: np.ndarray = cv2.medianBlur(cl1, 3)
            # Apply adaptive thresholding
            thresh: np.ndarray = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                          cv2.THRESH_BINARY_INV, 11, 2)
            text: str = pytesseract.image_to_string(thresh).strip()
            if text:
                return text
            else:
                return "Unknown Card"
        except Exception as e:
            self.logger.error(f"Error during card name identification: {e}")
            return f"Error identifying card name: {e}"

    def save_segmented_cards(self, segmentations: List[Dict[str, Any]], output_dir: str) -> None:
        """Saves the segmented card images to the specified directory.

        Args:
            segmentations: A list of card segmentation dictionaries.
            output_dir: The directory to save the segmented card images.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, segmentation in enumerate(segmentations):
            image: np.ndarray = segmentation["image"]
            card_name: str = segmentation.get("card_name", "Unknown Card")
            if card_name and card_name != "Unknown Card":
                filename: str = os.path.join(output_dir, f"{self.sanitize_filename(card_name)}.png")
            else:
                filename: str = os.path.join(output_dir, f"card_{i}.png")
            cv2.imwrite(filename, image)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitizes a string to be safe for use as a filename.

        Replaces any character that is not alphanumeric, underscore, or dot with an underscore.
        """
        return re.sub(r"[^a-zA-Z0-9_.]", "_", filename)