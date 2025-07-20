import unittest
import numpy as np
from PIL import Image
import io
import cv2

from processing_service.core.image_processing import (
    preprocess_image,
    segment_cards,
    ocr_card,
    process_image,
)


class TestImageProcessingLogic(unittest.TestCase):
    def test_segment_cards_with_multiple_cards(self):
        # Create a dummy image with two rectangles
        image = np.zeros((300, 400), dtype=np.uint8)
        cv2.rectangle(image, (20, 20), (150, 250), 255, -1)
        cv2.rectangle(image, (200, 50), (350, 200), 255, -1)

        card_images = segment_cards(image)
        self.assertEqual(len(card_images), 2)

    def test_process_image_with_no_cards(self):
        # Create a blank image
        image = Image.new("RGB", (100, 100), color="white")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()

        card_texts = process_image(image_bytes)
        self.assertEqual(len(card_texts), 0)


if __name__ == "__main__":
    unittest.main()
