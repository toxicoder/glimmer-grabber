import unittest
import cv2
import numpy as np
from noise_reducer import reduce_noise

class TestNoiseReducer(unittest.TestCase):
    def test_reduce_noise(self):
        # Create a dummy image with some random noise
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        noise = np.random.normal(0, 20, (100, 100, 3)).astype(np.uint8)
        noisy_image = cv2.add(image, noise)

        # Apply noise reduction
        denoised_image = reduce_noise(noisy_image)

        # Check if the output image has the same dimensions as the input
        self.assertEqual(denoised_image.shape, noisy_image.shape)
        self.assertEqual(denoised_image.dtype, noisy_image.dtype)

if __name__ == '__main__':
    unittest.main()
