import argparse
import os
import argparse
import os
import csv  # Import the csv module
from typing import List
from .config_manager import ConfigManager
from .image_reader import read_images_from_folder
from src.core.image_processor import process_images
from .card_data_fetcher import fetch_card_data  # Import the card_data_fetcher

def load_processed_images() -> List[str]:
    history_file: str = os.path.join("data", "processed_images.log")
    if not os.path.exists(history_file):
        return []
    with open(history_file, "r") as f:
        return [line.strip() for line in f]

processed_images: List[str] = load_processed_images()

def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments.

    Returns:
        An argparse.Namespace object containing the parsed arguments.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="CLI for processing card images.")
    parser.add_argument("input_dir", nargs='?', default="input", help="Path to the input directory.")
    parser.add_argument("output_dir", nargs='?', default="output", help="Path to the output directory.")
    parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")
    parser.add_argument("--save_segmented_images", action="store_true", help="Save segmented card images.")
    parser.add_argument("--save_segmented_images_path", help="Path to save segmented card images.")

    return parser.parse_args()

def generate_csv(card_data: List[dict], output_path: str) -> None:
    """Generates a CSV file from the fetched card data.

    Args:
        card_data: A list of dictionaries, where each dictionary represents a card.
        output_path: The path to the output directory.
    """
    n = 1
    while True:
        csv_file_path = os.path.join(output_path, f"lorcana_collection_{n}.csv")
        if not os.path.exists(csv_file_path):
            break
        n += 1

    # Generates a unique filename for the CSV output to prevent overwriting existing files.
    # The filename follows the format "lorcana_collection_{n}.csv", where 'n' is an incrementing number.
    # The function checks for existing files with this pattern and increments 'n' until a unique filename is found.
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames: list[str] = []
        if card_data:
            fieldnames = list(card_data[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(card_data)
    print(f"Card data saved to {csv_file_path}")


def main() -> None:
    """
    Main function to handle command-line arguments, process images, fetch card data, and generate a CSV.

    Program Flow:
    1. Parses command-line arguments using the `parse_arguments` function.
    2. Initializes a `ConfigManager` with the parsed arguments.
    3. Retrieves configuration values (input path, output path, etc.) from the `ConfigManager`.
    4. Prints the configuration settings being used.
    5. Reads image files from the specified input directory using `read_images_from_folder`.
    6. Processes the images using the `process_images` function, returning processed data.
    7. Fetches card data based on the processed images.
    8. Generates a CSV file from the fetched card data and saves it to the output directory.
    """
    args: argparse.Namespace = parse_arguments()
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

    # Call the process_images function and get the processed data
    processed_images = process_images(image_files, output_path, save_segmented_images, save_segmented_images_path)

    # Fetch card data using the processed data
    card_data: List[dict] = fetch_card_data(processed_images)

    # Generate CSV
    generate_csv(card_data, output_path)

if __name__ == "__main__":
    main()
