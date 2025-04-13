import unittest
import os
import numpy as np
from unittest.mock import patch, mock_open
from image_reader import read_images_from_folder, iterate_images

class TestImageReader(unittest.TestCase):
    """Tests for the image reading utility."""
    @patch('glob.glob')
    @patch('cv2.imread')
    def test_read_images_from_folder_success(self, mock_imread, mock_glob):
        """Test successful reading of images from a folder.

        This test checks if the function correctly reads image files from a specified
        folder. It mocks the `glob.glob` function to simulate finding image files and
        `cv2.imread` to simulate successful image reading. It then verifies that the
        function returns a list of images with the expected content.
        """
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
        """Test reading from an empty folder.

        This test checks the behavior of the function when no image files are found in
        the specified folder. It mocks the `glob.glob` function to simulate an empty
        folder and verifies that the function returns an empty list.
        """
        # Simulate no image files found
        mock_glob.return_value = []

        images = read_images_from_folder("test_folder")

        self.assertEqual(len(images), 0)

    @patch('glob.glob')
    @patch('cv2.imread')
    def test_read_images_from_folder_read_error(self, mock_imread, mock_glob):
        """Test handling of image reading errors.

        This test checks the behavior of the function when an error occurs while
        reading an image file. It mocks `glob.glob` to simulate finding an image file
        and `cv2.imread` to simulate a reading error (returning None). It then
        verifies that the function returns an empty list.
        """
        # Simulate finding one image file
        mock_glob.return_value = ["image1.jpg"]
        # Simulate error reading the image
        mock_imread.return_value = None

        images = read_images_from_folder("test_folder")

        self.assertEqual(len(images), 0)

    def test_iterate_images(self):
        """Test iterating through a list of images.

        This test checks if the `iterate_images` function correctly iterates through a
        list of images. It creates a list of dummy images, obtains an iterator using
        the function, and then verifies that the iterator yields the images in the
        correct order and raises a StopIteration exception when the end of the list is
        reached.
        """
        images = [np.zeros((100, 100, 3), dtype=np.uint8), np.ones((100, 100, 3), dtype=np.uint8)]

        image_gen = iterate_images(images)

        self.assertTrue(np.array_equal(next(image_gen), images[0]))
        self.assertTrue(np.array_equal(next(image_gen), images[1]))
        with self.assertRaises(StopIteration):
            next(image_gen)

if __name__ == '__main__':
    unittest.main()
