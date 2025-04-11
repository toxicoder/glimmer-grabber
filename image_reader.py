import cv2
import glob
import os

def read_images_from_folder(folder_path):
    """Reads image files (JPG, PNG) from the specified folder.

    Args:
        folder_path (str): The path to the folder containing the images.

    Returns:
        list: A list of images as NumPy arrays, or an empty list if no images
              are found or an error occurs.
    """
    image_list = []
    supported_extensions = [".jpg", ".jpeg", ".png"]
    try:
        for ext in supported_extensions:
            for filename in glob.glob(os.path.join(folder_path, f"*{ext}")):
                try:
                    img = cv2.imread(filename)
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

def iterate_images(image_list):
    """Iterates through a list of images.

    Args:
        image_list (list): A list of images (NumPy arrays).

    Yields:
        NumPy array: Each image in the list.
    """
    for image in image_list:
        yield image
