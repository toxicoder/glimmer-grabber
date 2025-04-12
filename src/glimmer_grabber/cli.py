import argparse
import os
from typing import List
from .config_manager import ConfigManager
from .image_reader import read_images_from_folder
from .image_processor import process_images  # Import the new function

def load_processed_images() -> List[str]:
    history_file: str = os.path.join("data", "processed_images.log")
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r") as f:
        return [line.strip() for line in f]

processed_images: List[str] = load_processed_images()  # Adding type hint here

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="CLI for processing card images.")
    parser.add_argument("input_dir", help="Path to the input directory.")
    parser.add_argument("output_dir", help="Path to the output directory.")
    parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")
    parser.add_argument("--save_segmented_images", action="store_true", help="Save segmented card images.")
    parser.add_argument("--save_segmented_images_path", help="Path to save segmented card images.")

    return parser.parse_args()

def main() -> None:
    """Main function to handle command-line arguments and process images."""
    args: argparse.Namespace = parse_arguments()  # Type hint already present
    config_manager: ConfigManager = ConfigManager(cli_args=args)

    input_path: str = config_manager.get_input_path()
    output_path: str = config_manager.get_output_path()
    keep_split_card_images: bool = config_manager.get_keep_split_card_images()
    crawl_directories: bool = config_manager.get_crawl_directories()
    save_segmented_images: bool = config_manager.get_save_segmented_images()
    save_segmented_images_path: str = config_manager.get_save_segmented_images_path()

    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_path}")
    print(f"Keep split card images: {keep_split_card_images}")
    print(f"Crawl subdirectories: {crawl_directories}")
    print(f"Save segmented images: {save_segmented_images}")
    print(f"Save segmented images path: {save_segmented_images_path}")

    image_files: List[str] = read_images_from_folder()

    # Call the new process_images function
    process_images(image_files, output_path, save_segmented_images, save_segmented_images_path)

if __name__ == "__main__":
    main()
