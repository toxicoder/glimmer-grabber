import cv2
import os
import logging
from typing import List, Optional, Dict, Any # Added Any for segmentations

# Application-specific imports
from src.core.card_segmenter import CardSegmenter
from src.core.exceptions import ImageProcessingError
from src.app.config_manager import ConfigManager # Import ConfigManager
from src.core.inference import run_inference # Import run_inference
# Required for ImagePreprocessor, though not directly instantiated here.
# CardSegmenter might instantiate it using the passed config_manager.
from src.core.image_preprocessor import ImagePreprocessor

# Module-level logger
logger = logging.getLogger(__name__)

def process_images(
    image_files: List[str],
    output_path_context: str, # Renamed to avoid confusion, primarily for context or if CardSegmenter needs it passed explicitly
    # save_segmented_images_flag is now implicitly handled by CardSegmenter via config_manager
    # save_segmented_images_path_val is also implicitly handled by CardSegmenter via config_manager
    config_manager: ConfigManager # Added ConfigManager
) -> List[Dict[str, Any]]:
    """
    Processes a list of image files to detect and segment cards.

    This function iterates through each image file path provided, reads the image,
    and then uses the `CardSegmenter` (configured via `config_manager`) to perform
    card detection and segmentation. It then uses `run_inference` which applies
    a confidence threshold (from `config_manager`) to the results.

    Args:
        image_files (List[str]): Paths to image files.
        output_path_context (str): Base output directory, mainly for context. Specific save paths
                                   for segmented images are now handled by CardSegmenter via ConfigManager.
        config_manager (ConfigManager): The application's configuration manager, used to
                                        configure CardSegmenter, ImagePreprocessor (if used by CardSegmenter),
                                        and the inference confidence threshold.
    Returns:
        List[Dict[str, Any]]: Filtered list of dictionaries with segmentation data.
    Raises:
        FileNotFoundError: If an image file is not found.
        ImageProcessingError: If an image cannot be read or processed.
        RuntimeError: Propagated from `CardSegmenter` or `run_inference`.
    """
    # Initialize CardSegmenter, passing the config_manager instance.
    # CardSegmenter's __init__ will use this to get its yolo_model_path and other settings.
    # It will also use config_manager to decide whether to save images and where.
    card_segmenter: CardSegmenter = CardSegmenter(config_manager=config_manager)

    # Get segmentation confidence threshold from config_manager for run_inference
    confidence_threshold = config_manager.get_segmentation_confidence_threshold()

    processed_data_list: List[Dict[str, Any]] = []

    for image_path in image_files:
        logger.info(f"Starting processing for image: {image_path}")
        abs_image_path = os.path.abspath(image_path)

        if not os.path.exists(abs_image_path):
            logger.error(f"Image file not found at resolved path: {abs_image_path}.")
            raise FileNotFoundError(f"Critical error: Image file not found at {abs_image_path}.")

        try:
            image: Optional[cv2.Mat] = cv2.imread(abs_image_path)
            if image is None:
                logger.error(f"Failed to read image at {abs_image_path}. It might be corrupted or an unsupported format.")
                raise ImageProcessingError(f"Error: Could not read image at {abs_image_path} (corrupted or unsupported format).")

            logger.debug(f"Successfully read image: {image_path} (resolved: {abs_image_path})")

            # Perform card segmentation and inference using run_inference
            # run_inference internally calls card_segmenter.segment_cards and then filters.
            # CardSegmenter uses its own config_manager for its settings (model path, save paths etc.)
            segmentation_data: List[Dict[str, Any]] = run_inference(
                image,
                card_segmenter,
                confidence_threshold
            )

            logger.debug(f"Inference completed for {image_path}. Found {len(segmentation_data)} segments meeting threshold.")

            processed_data_list.append({
                "image_path": image_path,
                "segmentations": segmentation_data
            })

        except cv2.error as e:
            logger.error(f"An OpenCV error occurred while processing image {image_path}: {e}", exc_info=True)
            raise ImageProcessingError(f"OpenCV error processing image {image_path}: {e}")
        except ImageProcessingError:
            logger.error(f"Propagating ImageProcessingError for image {image_path}.", exc_info=True)
            raise
        except RuntimeError as e:
            logger.error(f"A runtime error occurred during segmentation of {image_path}: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing image {image_path}: {e}", exc_info=True)
            raise ImageProcessingError(f"An unexpected error occurred during processing of {image_path}: {e}")

    logger.info(f"Finished processing all {len(image_files)} specified image files. {len(processed_data_list)} have segmentation data.")
    return processed_data_list
