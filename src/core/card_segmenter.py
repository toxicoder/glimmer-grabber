# Standard library imports
import logging
import os
import re
from typing import Any, Dict, List, Optional

# Third-party imports
import cv2
import numpy as np
import pytesseract # For OCR

# Application-specific imports
from src.app.config_manager import ConfigManager
# Assuming ConfigManager is appropriately structured for type hinting and usage.

# Module-level logger
logger = logging.getLogger(__name__)

class CardSegmenter:
    """
    Segments cards from an image using a YOLOv8 model and identifies them using OCR.

    This class encapsulates the functionality for detecting card-like objects within
    an input image, segmenting these objects, and then attempting to identify
    the name of each card using Tesseract OCR on the segmented image portion.

    The segmentation process involves:
    1.  Loading a pre-trained YOLOv8 segmentation model.
    2.  Running inference on the input image to get segmentation masks and bounding boxes.
    3.  Cropping each detected card using its bounding box.
    4.  Passing the cropped card image to an OCR process for name identification.

    The OCR process involves:
    1.  Converting the cropped card image to grayscale.
    2.  Applying contrast enhancement (CLAHE).
    3.  Applying median blur for noise reduction.
    4.  Using adaptive thresholding to binarize the image.
    5.  Extracting text using Pytesseract.

    Configuration for saving segmented images is handled via a `ConfigManager` instance.

    Attributes:
        model: An instance of the YOLO model from `ultralytics` used for segmentation.
        config_manager (ConfigManager): Manages application configuration,
                                        particularly for saving segmented images.
    """

    def __init__(self, config_manager: Optional[ConfigManager] = None) -> None:
        """
        Initializes the CardSegmenter with a YOLOv8-seg model and a ConfigManager.
        The YOLO model path is now fetched from the ConfigManager.

        Args:
            config_manager (Optional[ConfigManager]): An instance of `ConfigManager`.
                                                      If None, a default `ConfigManager` will be instantiated.
        Raises:
            ImportError: If the `ultralytics` package is not installed.
            Exception: If the YOLO model fails to load.
        """
        # If config_manager is None, a default one is created.
        # This internal ConfigManager will load "config.json" by default
        # and use the yolo_model_path from that config or its own default.
        self.config_manager = config_manager if config_manager is not None else ConfigManager()

        # Get YOLO model path from the config_manager
        model_path_to_load = self.config_manager.get_yolo_model_path()
        logger.info(f"CardSegmenter attempting to load YOLO model from path: '{model_path_to_load}' (via ConfigManager)")

        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path_to_load)
            logger.info(f"Successfully loaded YOLOv8 model from '{model_path_to_load}'")
        except ImportError:
            logger.error("Ultralytics package not found. Please install 'ultralytics' to use YOLOv8.")
            raise ImportError("The 'ultralytics' package is required for CardSegmenter. Please install it.")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model from '{model_path_to_load}': {e}", exc_info=True)
            raise # Re-raise the exception to indicate failure in initialization

    def segment_cards(self, image: np.ndarray, original_image_path: str) -> List[Dict[str, Any]]:
        """
        Detects and segments cards in an image, then identifies them.
        If configured, saves individual segmented card images.

        Args:
            image (np.ndarray): The input image as a NumPy array (BGR format expected by OpenCV).
            original_image_path (str): The file path of the original image, used for naming saved segments.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries. Each dictionary represents a
            detected and processed card and typically contains:
                - "mask" (np.ndarray): The binary segmentation mask for the card.
                - "bbox" (np.ndarray): The bounding box coordinates [x1, y1, x2, y2].
                - "image" (np.ndarray): The cropped image of the segmented card.
                - "card_name" (str): The identified name of the card via OCR.
            Returns an empty list if no cards are detected or if an error occurs during prediction.

        Raises:
            RuntimeError: If a critical error occurs during the YOLO model prediction
                          or subsequent processing steps that prevents segmentation.
        """
        logger.info("Starting card segmentation process for the provided image.")
        try:
            # Perform prediction using the YOLO model.
            # `predict` can be configured further (e.g. confidence threshold) if needed.
            results = self.model.predict(image, verbose=False) # verbose=False to reduce Ultralytics' own console output

            # Check if results, masks, and boxes are present
            if results and results[0].masks is not None and results[0].boxes is not None:
                masks_data: np.ndarray = results[0].masks.data.cpu().numpy()
                boxes_data: np.ndarray = results[0].boxes.xyxy.cpu().numpy()
                # Get confidence scores if available (YOLOv8 typically provides these)
                confidence_scores: Optional[np.ndarray] = None
                if results[0].boxes.conf is not None:
                    confidence_scores = results[0].boxes.conf.cpu().numpy()

                segmentations: List[Dict[str, Any]] = []
                logger.info(f"Detected {len(masks_data)} potential card instances in the image.")

                for i in range(len(masks_data)):
                    current_mask: np.ndarray = masks_data[i]
                    current_bbox: np.ndarray = boxes_data[i]
                    current_confidence: Optional[float] = confidence_scores[i] if confidence_scores is not None else None

                    segmentation_info: Dict[str, Any] = {
                        "mask": current_mask,
                        "bbox": current_bbox,
                        "confidence": current_confidence # Include confidence in the output
                    }

                    # Extract bounding box coordinates as integers
                    x1, y1, x2, y2 = map(int, current_bbox)
                    logger.debug(f"Processing instance {i+1}/{len(masks_data)}: BBox [{x1}, {y1}, {x2}, {y2}]")

                    # Validate bounding box coordinates to ensure they are within image bounds and valid
                    if not (0 <= x1 < x2 <= image.shape[1] and 0 <= y1 < y2 <= image.shape[0]):
                        logger.warning(f"Bounding box for instance {i+1} is invalid or out of bounds: "
                                       f"x1={x1}, y1={y1}, x2={x2}, y2={y2} for image shape {image.shape}. Skipping this instance.")
                        continue # Skip this instance if BBox is invalid

                    # Crop the segmented card image using the bounding box
                    segmented_image: np.ndarray = image[y1:y2, x1:x2]
                    segmentation_info["image"] = segmented_image

                    # Identify card name using OCR on the segmented image
                    card_name: str = self.identify_card_name(segmented_image)
                    segmentation_info["card_name"] = card_name
                    logger.debug(f"Instance {i+1} identified as: '{card_name}'")

                    segmentations.append(segmentation_info)

                    segmentation_info["card_name"] = card_name
                    logger.debug(f"Instance {i+1} identified as: '{card_name}'")

                    # Save the individual segmented card image if configured
                    if self.config_manager.get_save_segmented_images():
                        self._save_individual_card_image(
                            segmented_image,
                            original_image_path,
                            i, # index
                            card_name
                        )

                    segmentations.append(segmentation_info)

                # The old self.save_segmented_cards(segmentations, output_dir) is removed
                # as saving now happens per card within the loop.

                logger.info(f"Successfully processed {len(segmentations)} card instances from the image.")
                return segmentations
            else:
                # Log if no cards were detected or if the model prediction yielded no usable results
                logger.info("No cards detected in the image, or the model prediction returned no segmentation data.")
                return []
        except Exception as e:
            # Log any other unexpected error during segmentation
            logger.error(f"An error occurred during the card segmentation process: {e}", exc_info=True)
            # Propagate as a runtime error to signal failure
            raise RuntimeError(f"Segmentation failed due to an internal error: {e}")

    def identify_card_name(self, image: np.ndarray) -> str:
        """
        Identifies the card name from a segmented card image using OCR.

        The process involves several image preprocessing steps before applying Tesseract OCR:
        1. Convert to grayscale.
        2. Apply Contrast Limited Adaptive Histogram Equalization (CLAHE).
        3. Apply Median Blur for noise reduction.
        4. Apply Adaptive Thresholding to binarize the image.
        5. Extract text using pytesseract.

        Args:
            image (np.ndarray): The segmented card image (BGR format).

        Returns:
            str: The identified card name. Returns "Unknown Card" if OCR fails to extract
                 text, "Unknown Card (Empty Segment)" if the input image is empty,
                 or "Error: Tesseract Not Found" if Tesseract is not installed/configured,
                 or "Error Identifying Card Name" for other OCR errors.
        """
        logger.debug("Starting card name identification via OCR.")
        try:
            # Check if the input image is empty
            if image.size == 0:
                logger.warning("Cannot identify card name: input image segment is empty.")
                return "Unknown Card (Empty Segment)"

            # Convert image to grayscale
            gray_image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Get OCR preprocessing parameters from config or use defaults
            ocr_prep_settings = self.config_manager.get_image_preprocessing_settings().get("ocr_preprocessing", {})

            clahe_clip_limit = ocr_prep_settings.get("clahe_clip_limit", 2.0)
            clahe_tile_grid_size = tuple(ocr_prep_settings.get("clahe_tile_grid_size", [8, 8])) # Ensure tuple
            median_blur_ksize = ocr_prep_settings.get("median_blur_ksize", 3)
            adaptive_thresh_block_size = ocr_prep_settings.get("adaptive_thresh_block_size", 11)
            adaptive_thresh_C = ocr_prep_settings.get("adaptive_thresh_C", 2)

            logger.debug(f"OCR Preprocessing: CLAHE clipLimit={clahe_clip_limit}, tileGridSize={clahe_tile_grid_size}")
            logger.debug(f"OCR Preprocessing: MedianBlur ksize={median_blur_ksize}")
            logger.debug(f"OCR Preprocessing: AdaptiveThreshold blockSize={adaptive_thresh_block_size}, C={adaptive_thresh_C}")

            # Apply CLAHE for contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=clahe_clip_limit, tileGridSize=clahe_tile_grid_size)
            contrast_enhanced_image: np.ndarray = clahe.apply(gray_image)

            # Apply median blur for noise reduction
            # Ensure ksize is odd and > 1 for medianBlur
            if median_blur_ksize < 3 or median_blur_ksize % 2 == 0:
                logger.warning(f"Median blur ksize {median_blur_ksize} is invalid. Must be odd and >= 3. Defaulting to 3.")
                median_blur_ksize = 3
            blurred_image: np.ndarray = cv2.medianBlur(contrast_enhanced_image, median_blur_ksize)

            # Apply adaptive thresholding to binarize the image
            # Ensure block_size is odd and > 1
            if adaptive_thresh_block_size < 3 or adaptive_thresh_block_size % 2 == 0:
                logger.warning(f"Adaptive threshold block_size {adaptive_thresh_block_size} is invalid. Must be odd and >= 3. Defaulting to 11.")
                adaptive_thresh_block_size = 11
            thresholded_image: np.ndarray = cv2.adaptiveThreshold(
                blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, adaptive_thresh_block_size, adaptive_thresh_C
            )

            # For debugging Tesseract setup, uncomment these lines:
            # logger.debug(f"Tesseract version: {pytesseract.get_tesseract_version()}")
            # logger.debug(f"Tesseract command path: {pytesseract.pytesseract.tesseract_cmd}")

            # Extract text using Tesseract OCR
            # Configuration options for Pytesseract can be added here if needed (e.g., --psm)
            extracted_text: str = pytesseract.image_to_string(thresholded_image).strip()

            if extracted_text:
                logger.debug(f"OCR extracted text: '{extracted_text}'")
                return extracted_text
            else:
                logger.debug("OCR extracted no text from the image segment.")
                return "Unknown Card"
        except pytesseract.TesseractNotFoundError:
            # Handle cases where Tesseract is not installed or not found in PATH
            logger.error("Tesseract is not installed or not found in your system's PATH. OCR cannot proceed.", exc_info=True)
            return "Error: Tesseract Not Found" # Specific error message for Tesseract missing
        except Exception as e:
            # Handle any other errors during the OCR process
            logger.error(f"An error occurred during card name identification (OCR): {e}", exc_info=True)
            return "Error Identifying Card Name" # Generic error for other OCR issues

    def _save_individual_card_image(
        self,
        card_image: np.ndarray,
        original_image_path: str,
        card_index: int,
        identified_card_name: str
    ) -> None:
        """
        Saves an individual segmented card image to disk.

        The save path and filename are determined by configuration and input parameters.
        This method is called internally by `segment_cards` if saving is enabled.

        Args:
            card_image (np.ndarray): The NumPy array of the segmented card image.
            original_image_path (str): Path to the original full image from which this card was segmented.
            card_index (int): The index of this card within the detections from the original image.
            identified_card_name (str): The name of the card as identified by OCR.
        """
        save_path_base = self.config_manager.get_save_segmented_images_path()
        if not save_path_base:
            logger.warning("Save segmented images path is not configured. Cannot save individual card image.")
            # Attempt to use a default subfolder in the main output_path
            main_output_path = self.config_manager.get_output_path()
            if main_output_path:
                save_path_base = os.path.join(main_output_path, "segmented_cards_default")
                logger.info(f"Defaulting save path for segmented images to: '{save_path_base}'")
            else:
                logger.error("Main output path is not configured. Cannot determine a save location for segmented images.")
                return

        try:
            os.makedirs(save_path_base, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create directory '{save_path_base}' for segmented card: {e}", exc_info=True)
            return

        original_basename = os.path.splitext(os.path.basename(original_image_path))[0]
        safe_card_name = self.sanitize_filename(identified_card_name if identified_card_name and identified_card_name.strip() else f"Unknown_Card")

        # Construct filename: {original_image_name_without_extension}_card_{index}_{card_name}.png
        filename = f"{original_basename}_card_{card_index}_{safe_card_name}.png"
        full_save_path = os.path.join(save_path_base, filename)

        try:
            cv2.imwrite(full_save_path, card_image)
            logger.info(f"Saved segmented card image to: '{full_save_path}'")
        except cv2.error as e:
            logger.error(f"OpenCV error saving image '{full_save_path}': {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Failed to save segmented card image '{full_save_path}': {e}", exc_info=True)


    def sanitize_filename(self, filename_str: str) -> str:
        """
        Sanitizes a string to make it safe for use as a filename.

        This involves:
        1. Replacing any character that is not alphanumeric, underscore, dot, or hyphen
           with an underscore.
        2. Replacing multiple consecutive underscores with a single underscore.
        3. Stripping leading/trailing problematic characters (underscore, dot, hyphen).
        4. Ensuring the filename is not empty (defaults to "invalid_name" if it becomes empty).
        5. Truncating the filename to a maximum length (default 200 characters) to prevent
           issues with filesystem limits.

        Args:
            filename_str (str): The input string to sanitize.

        Returns:
            str: The sanitized string, safe for use as a filename.
        """
        # Define a conservative maximum filename length
        max_length = 200

        # Replace characters not allowed in filenames with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename_str)
        # Collapse multiple consecutive underscores into one
        sanitized = re.sub(r"__+", "_", sanitized)
        # Remove leading or trailing underscores, dots, or hyphens
        sanitized = sanitized.strip('_.-')

        # If the sanitization results in an empty string, provide a default name
        if not sanitized:
            sanitized = "invalid_name"

        # Truncate to maximum length
        return sanitized[:max_length]