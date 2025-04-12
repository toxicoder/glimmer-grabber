import unittest
import os
import numpy as np
from unittest.mock import patch, mock_open
from image_reader import read_images_from_folder, iterate_images

class TestImageReader(unittest.TestCase):
    @patch('glob.glob')
    @patch('cv2.imread')
    def test_read_images_from_folder_success(self, mock_imread, mock_glob):
        # Simulate finding two image files
        mock_glob.return_value = ["image1.jpg", "image2.png"]
        # Simulate reading images successfully
        mock_imread.side_effect = [np.zeros((100, 100, 3), dtype=np.uint8), np.ones((100, 100, 3), dtype=np.uint8)]
        
        images = read_images_from_folder("test_folder")
        
        self.assertEqual(len(images), 2)
        self.assertTrue(np.array_equal(images[0], np.zeros((100, 100, 3), dtype=np.uint8)))
        self.assertTrue(np.array_equal(images[1], np.ones((100, 100, 3), dtype=np.uint8)))

    @patch('glob.glob')
    def test_read_images_from_folder_empty(self, mock_glob):
        # Simulate no image files found
        mock_glob.return_value = []
        
        images = read_images_from_folder("test_folder")
        
        self.assertEqual(len(images), 0)

    @patch('glob.glob')
    @patch('cv2.imread')
    def test_read_images_from_folder_read_error(self, mock_imread, mock_glob):
        # Simulate finding one image file
        mock_glob.return_value = ["image1.jpg"]
        # Simulate error reading the image
        mock_imread.return_value = None
        
        images = read_images_from_folder("test_folder")
        
        self.assertEqual(len(images), 0)

    def test_iterate_images(self):
        images = [np.zeros((100, 100, 3), dtype=np.uint8), np.ones((100, 100, 3), dtype=np.uint8)]
        
        image_gen = iterate_images(images)
        
        self.assertTrue(np.array_equal(next(image_gen), images[0]))
        self.assertTrue(np.array_equal(next(image_gen), images[1]))
        with self.assertRaises(StopIteration):
            next(image_gen)

if __name__ == '__main__':
    unittest.main()
