import unittest
import numpy as np
from PIL import Image
import io

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
        # Create a dummy image
        image = np.zeros((200, 200), dtype=np.uint8)
        card_images = segment_cards(image)
        self.assertIsInstance(card_images, list)
        self.assertGreater(len(card_images), 0)
        self.assertIsInstance(card_images[0], np.ndarray)

    def test_ocr_card(self):
        # Create a dummy image with some text
        image = Image.new("L", (200, 50), color=255)
        # This test requires tesseract to be installed and configured.
        # For now, we'll just test that it returns a string.
        # A more robust test would involve a known image and expected text.
        text = ocr_card(np.array(image))
        self.assertIsInstance(text, str)


if __name__ == "__main__":
    unittest.main()
