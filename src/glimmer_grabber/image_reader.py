import cv2
import glob
import os
import numpy as np
from typing import List, Iterator, Optional
from .config_manager import ConfigManager

def read_images_from_folder() -> List[np.ndarray]:
    """
    Reads image files (JPG, JPEG, PNG) from the input directory specified in the configuration.
    Handles crawling of subdirectories based on the configuration.

    Returns:
        List[np.ndarray]: A list of images as NumPy arrays.
                         Returns an empty list if no images are found or if an error occurs.
    """
    config_manager: ConfigManager = ConfigManager()
    folder_path: Optional[str] = config_manager.get_input_path()
    crawl_subdirectories: Optional[bool] = config_manager.get_crawl_directories()

    if not folder_path:
        print("Error: Input directory not specified in configuration.")
        return []

    image_list: List[np.ndarray] = []
    supported_extensions: List[str] = [".jpg", ".jpeg", ".png"]
    search_pattern: str = "**/*" if crawl_subdirectories else "*"

    try:
        for ext in supported_extensions:
            for filename in glob.glob(os.path.join(folder_path, f"{search_pattern}{ext}"), recursive=bool(crawl_subdirectories)):
                try:
                    img: Optional[np.ndarray] = cv2.imread(filename)
                    if img is not None:
                        image_list.append(img)
                    else:
                        print(f"Error: Could not read image file: {filename}")
                except Exception as e:
                    print(f"Error reading image file {filename}: {e}")
        return image_list
    except Exception as e:
        print(f"Error accessing folder {folder_path}: {e}")
        return []

def iterate_images(image_list: List[np.ndarray]) -> Iterator[np.ndarray]:
    """
    Iterates through a list of images.

    Args:
        image_list (List[np.ndarray]): A list of images as NumPy arrays.

    Yields:
        np.ndarray: Each image in the list.
    """
    for image in image_list:
        yield image
