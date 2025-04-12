import argparse
import os
from .config_manager import ConfigManager
from .image_reader import read_images_from_folder

def load_processed_images():
    history_file = os.path.join("data", "processed_images.log")
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r") as f:
        return [line.strip() for line in f]

processed_images = load_processed_images()

def parse_arguments():
    parser = argparse.ArgumentParser(description="CLI for processing card images.")
    parser.add_argument("input_dir", help="Path to the input directory.")
    parser.add_argument("output_dir", help="Path to the output directory.")
    parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")
    parser.add_argument("--save_segmented_images", action="store_true", help="Save segmented card images.")
    parser.add_argument("--save_segmented_images_path", help="Path to save segmented card images.")

    return parser.parse_args()

def main():
    args = parse_arguments()
    config_manager = ConfigManager(cli_args=args)

    input_path = config_manager.get_input_path()
    output_path = config_manager.get_output_path()
    keep_split_card_images = config_manager.get_keep_split_card_images()
    crawl_directories = config_manager.get_crawl_directories()
    save_segmented_images = config_manager.get_save_segmented_images()
    save_segmented_images_path = config_manager.get_save_segmented_images_path()

    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_path}")
    print(f"Keep split card images: {keep_split_card_images}")
    print(f"Crawl subdirectories: {crawl_directories}")
    print(f"Save segmented images: {save_segmented_images}")
    print(f"Save segmented images path: {save_segmented_images_path}")

    image_files = read_images_from_folder()

    from src.core.card_segmenter import CardSegmenter  # Import here to avoid circular import
    card_segmenter = CardSegmenter()

    with open(os.path.join("data", "processed_images.log"), "a") as f:
        for image_path in image_files:
            if image_path in processed_images:
                print(f"Skipping already processed image: {image_path}")
                continue

            print(f"Processing image: {image_path}")
            try:
                # Read the image using cv2
                import cv2
                image = cv2.imread(image_path)
                if image is None:
                    print(f"Error: Could not read image at {image_path}")
                    continue

                # Perform card segmentation
                segmentations = card_segmenter.segment_cards(image)

                f.write(image_path + "\n")
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")

if __name__ == "__main__":
    main()
