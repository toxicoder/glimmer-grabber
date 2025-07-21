import unittest
import numpy as np
from PIL import Image
import io
import cv2

from fuzzywuzzy import fuzz

from processing_service.core.image_processing import (
    preprocess_image,
    segment_cards,
    ocr_card,
)


class TestCoreImageProcessing(unittest.TestCase):
    def test_preprocess_image(self):
        # Create a dummy image
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()

        preprocessed_image = preprocess_image(image_bytes)
        self.assertIsInstance(preprocessed_image, np.ndarray)
        self.assertEqual(len(preprocessed_image.shape), 2)  # Grayscale

    def test_segment_cards(self):
        # Create a dummy image with a black rectangle on a white background
        image = np.full((200, 200), 255, dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (150, 150), 0, -1)
        card_images = segment_cards(image)
        self.assertIsInstance(card_images, list)
        self.assertGreater(len(card_images), 0)
        self.assertIsInstance(card_images[0], np.ndarray)

    def test_ocr_card(self):
        # Load the test image
        image = Image.open("processing_service/test_image.png")
        # Convert the image to a numpy array
        image_np = np.array(image)
        # Perform OCR on the image
        text = ocr_card(image_np)
        # Check that the OCR text is correct
        self.assertGreater(fuzz.ratio(text.strip(), "Hello, World!"), 80)


if __name__ == "__main__":
    unittest.main()
