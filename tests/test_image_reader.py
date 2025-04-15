import unittest
import os
import numpy as np
import cv2
import tempfile
from src.app.image_reader import read_images_from_folder, iterate_images
from unittest.mock import patch

from src.app.config_manager import ConfigManager

class TestImageReader(unittest.TestCase):
    """Tests for the image reading utility."""
    def test_read_images_from_folder_success(self):
        """Test successful reading of images from a folder.

        This test checks if the function correctly reads image files.
        It uses a temporary directory and verifies the function's output.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(ConfigManager, "get_input_path", return_value=temp_dir):
                # Create dummy image files
                image1_path = os.path.join(temp_dir, "image1.jpg")
                image2_path = os.path.join(temp_dir, "image2.png")
                # Create a dummy image - a small colored square
                dummy_image1 = np.zeros((10, 10, 3), dtype=np.uint8)
                dummy_image1[:] = (0, 0, 255)  # Blue
                dummy_image2 = np.zeros((10, 10, 3), dtype=np.uint8)
                dummy_image2[:] = (0, 255, 0)  # Green
                # Save the dummy images using cv2.imwrite
                cv2.imwrite(image1_path, dummy_image1)
                cv2.imwrite(image2_path, dummy_image2)

                images = read_images_from_folder()

                self.assertEqual(len(images), 2)
                # Check if the images are read correctly, compare to the dummy images
                self.assertTrue(all(isinstance(img, np.ndarray) for img in images))  # Check if all elements are numpy arrays
                self.assertTrue(np.array_equal(images[0], dummy_image1))
                self.assertTrue(np.array_equal(images[1], dummy_image2))

    def test_read_images_from_folder_empty(self):
        """Test reading from an empty folder.

        This test checks the behavior of the function when no image files are found.
        It uses a temporary directory and verifies that the function returns an empty list.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(ConfigManager, "get_input_path", return_value=temp_dir):
                images = read_images_from_folder()
                self.assertEqual(len(images), 0)

    def test_read_images_from_folder_read_error(self):
        """Test handling of image reading errors.

        This test checks the behavior of the function when an error occurs while
        reading an image file. It creates a temporary directory and adds a file that
        is not a valid image. It then verifies that the function returns an empty list.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(ConfigManager, "get_input_path", return_value=temp_dir):
                # Create a file that is not a valid image
                invalid_image_path = os.path.join(temp_dir, "invalid_image.txt")
                with open(invalid_image_path, "w") as f:
                    f.write("This is not an image.")

                images = read_images_from_folder()
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
