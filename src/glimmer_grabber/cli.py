import argparse
import os
from .config_manager import ConfigManager
from .image_reader import read_images_from_folder

def parse_arguments():
    parser = argparse.ArgumentParser(description="CLI for processing card images.")
    parser.add_argument("input_dir", help="Path to the input directory.")
    parser.add_argument("output_dir", help="Path to the output directory.")
    parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")

    return parser.parse_args()

def main():
    args = parse_arguments()
    config_manager = ConfigManager(cli_args=args)

    input_path = config_manager.get_input_path()
    output_path = config_manager.get_output_path()
    keep_split_card_images = config_manager.get_keep_split_card_images()
    crawl_directories = config_manager.get_crawl_directories()

    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_path}")
    print(f"Keep split card images: {keep_split_card_images}")
    print(f"Crawl subdirectories: {crawl_directories}")

    history_file = os.path.join("data", "processed_images.txt")
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            pass

    image_files = read_images_from_folder()

    with open(history_file, "r") as f:
        processed_images = [line.strip() for line in f]

    with open(history_file, "a") as f:
        for image_path in image_files:
            image_name = os.path.basename(image_path)
            if image_name in processed_images:
                print(f"Skipping already processed image: {image_name}")
                continue

            print(f"Processing image: {image_name}")
            #  processed_image = process_image(image_path)

            f.write(image_name + "\n")

if __name__ == "__main__":
    main()
