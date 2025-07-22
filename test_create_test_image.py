import unittest
import os
import subprocess

class TestCreateImage(unittest.TestCase):

    def test_create_image(self):
        # Run the script
        subprocess.run(["python", "create_test_image.py"])

        # Check that the image was created
        self.assertTrue(os.path.exists("processing_service/test_image.png"))

if __name__ == '__main__':
    unittest.main()
