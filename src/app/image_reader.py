# Standard library imports
import glob
import logging
import os
from typing import Iterator, List, Optional # Iterator and Optional are used

# Third-party imports
import cv2 # OpenCV import is not strictly necessary here if only paths are returned
import numpy as np # NumPy import is not strictly necessary if only paths are returned

# Application-specific imports
from .config_manager import ConfigManager # For accessing configuration settings

# Module-level logger
logger = logging.getLogger(__name__)

def read_images_from_folder() -> List[str]:
    """
    Scans a specified directory for image files and returns a list of their paths.

    This function retrieves the input directory path and crawl settings from the
    `ConfigManager`. It then searches for image files with common extensions
    (JPG, JPEG, PNG) within this directory. If configured, it will also search
    recursively through subdirectories.

    The function returns a list of absolute paths to the found image files.
    Image loading itself is deferred to other parts of the application to manage
    memory more effectively.

    Note:
        A `ConfigManager` instance is created internally. In applications with
        a central configuration object, consider passing `ConfigManager` as an
        argument to avoid multiple instantiations.

    Returns:
        List[str]: A list of absolute file paths for the images found.
                   Returns an empty list if the input directory is not specified,
                   does not exist, or if no supported image files are found.
                   Also returns an empty list on encountering other access errors.
    """
    # Instantiate ConfigManager to get folder path and crawl settings.
    # This is a local instantiation; consider passing as an argument if ConfigManager
    # is already instantiated elsewhere in the application lifecycle.
    config_manager: ConfigManager = ConfigManager()
    folder_path: Optional[str] = config_manager.get_input_path()
    crawl_subdirectories: bool = config_manager.get_crawl_directories() # Defaults to True in ConfigManager

    # Validate that the folder_path is configured
    if not folder_path:
        logger.error("Input directory not specified in configuration. Cannot read images.")
        return []

    # Validate that the folder_path actually exists and is a directory
    if not os.path.isdir(folder_path):
        logger.error(f"Input directory '{folder_path}' does not exist or is not a directory.")
        return []

    logger.info(f"Reading image file paths from folder: '{folder_path}' (Crawl subdirectories: {crawl_subdirectories})")

    image_paths: List[str] = []
    # Define list of supported image file extensions
    supported_extensions: List[str] = [".jpg", ".jpeg", ".png"]

    # Ensure the base path for glob search is absolute for consistent behavior
    base_path = os.path.abspath(folder_path)

    try:
        # Iterate over each supported extension to find matching files
        for ext in supported_extensions:
            # Construct the search pattern for glob
            # If crawling subdirectories, use '**/*' to match files in any subdirectory.
            # Otherwise, use '*' to match files only in the top-level directory.
            pattern = os.path.join(base_path, f'**/*{ext}' if crawl_subdirectories else f'*{ext}')
            logger.debug(f"Searching for images with pattern: '{pattern}', recursive={crawl_subdirectories}")

            # Use glob to find all files matching the pattern.
            # `recursive=True` is necessary for the `**` wildcard to work correctly.
            # glob.glob returns absolute paths if `base_path` is absolute.
            found_files = glob.glob(pattern, recursive=crawl_subdirectories)

            for filename in found_files:
                # Ensure that the found path is a file (and not a directory that might match the pattern by chance)
                if os.path.isfile(filename):
                    image_paths.append(filename)
                else:
                    # Log if a directory was matched, which is usually not intended for image files
                    logger.debug(f"Path '{filename}' matched pattern but is a directory, skipping.")

        # Log summary of findings
        if not image_paths:
            logger.info(f"No image files with supported extensions found in '{base_path}'.")
        else:
            logger.info(f"Found {len(image_paths)} image file(s) in '{base_path}'.")
            # Log a few found paths for debugging if necessary (e.g., first 3)
            for i, path_to_log in enumerate(image_paths[:3]):
                logger.debug(f"  Example found image path {i+1}: {path_to_log}")

        return image_paths # Return the list of found image paths

    except Exception as e:
        # Catch any other exceptions during folder access or globbing
        logger.error(f"Error accessing folder or reading files in '{base_path}': {e}", exc_info=True)
        return [] # Return empty list in case of error

# Note on `iterate_images`:
# This function was originally designed to iterate over a list of loaded NumPy image arrays.
# However, `read_images_from_folder` has been updated to return a list of file paths (`List[str]`)
# to improve memory efficiency by deferring image loading.
# The `process_images` function in `src/core/image_processor.py` now expects these paths.
# As such, `iterate_images` in its current form (expecting List[np.ndarray]) is likely
# unused in the main application flow. It's kept here for now but might be deprecated
# or refactored if image iteration is needed differently.

def iterate_images(image_list: List[np.ndarray]) -> Iterator[np.ndarray]:
    """
    Iterates through a list of images (NumPy arrays).

    This function provides an iterator for a list of images, allowing for
    sequential access to each image in the list.

    Args:
        image_list (List[np.ndarray]): A list of images, where each image is
                                       represented as a NumPy array.

    Yields:
        np.ndarray: Each image from the `image_list` in sequence.

    Warning:
        This function expects a list of loaded images (NumPy arrays).
        Given that `read_images_from_folder` now returns paths, this function
        might be deprecated or require changes if image iteration is needed
        based on loaded images rather than paths.
    """
    if not image_list:
        logger.debug("iterate_images called with an empty list.")
        return

    logger.debug(f"Iterating over a list of {len(image_list)} images.")
    for i, image in enumerate(image_list):
        logger.debug(f"Yielding image {i+1}/{len(image_list)} from iterator.")
        yield image
