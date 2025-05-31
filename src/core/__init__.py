# src/core/__init__.py

"""
Core Processing Package for GlimmerGrabber.

This package encapsulates the primary image processing functionalities of the
application. It includes modules for segmenting cards from images, preprocessing
these images to improve clarity, running inference models (though currently,
segmentation is the main inference step), and orchestrating the overall
image processing pipeline.

Modules within this package:
- `card_segmenter`: Contains `CardSegmenter` class for detecting and segmenting
  card instances from an image using a YOLO model and then identifying card
  names via OCR.
- `image_preprocessor`: Provides the `ImagePreprocessor` class, which applies
  a configurable sequence of image transformations (e.g., noise reduction,
  illumination normalization) based on utility functions from `src.utils`.
- `image_processor`: Home to the `process_images` function, which orchestrates
  the reading of image files, their processing via `CardSegmenter` (which
  includes segmentation and OCR), and returns structured data.
- `inference`: Currently contains `run_inference`, a wrapper function that uses
  `CardSegmenter` to get segmentation results and applies a confidence filter.
  This module could be expanded for other types of model inference in the future.
- `exceptions`: Defines custom exceptions, like `ImageProcessingError`, specific
  to errors encountered during core image processing tasks.

The typical workflow involves `image_processor.process_images` calling upon
`CardSegmenter` (which might implicitly use `ImagePreprocessor` or its utilities
if integrated for OCR preprocessing) to get card details.
"""

# Example of how components might be exposed (optional, currently commented out):
# If you want to allow imports like `from src.core import CardSegmenter`
# instead of `from src.core.card_segmenter import CardSegmenter`, uncomment relevant lines.

# from .card_segmenter import CardSegmenter
# from .image_preprocessor import ImagePreprocessor
# from .image_processor import process_images
# from .inference import run_inference
# from .exceptions import ImageProcessingError

# To control what `from src.core import *` imports (generally discouraged):
# __all__ = [
#     "CardSegmenter",
#     "ImagePreprocessor",
#     "process_images",
#     "run_inference",
#     "ImageProcessingError",
# ]
