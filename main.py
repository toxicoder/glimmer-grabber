import argparse
from config_manager import ConfigManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Card processing application.")
    parser.add_argument("--input-dir", required=True, help="Path to the input directory.")
    parser.add_argument("--output-dir", required=True, help="Path to the output directory.")
    parser.add_argument("--keep-split-card-images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl-directories", action="store_true", default=True, help="Crawl subdirectories.")

    args = parser.parse_args()
    cli_args = vars(args)

    config_manager = ConfigManager(cli_args=cli_args)

    # Now you can use config_manager to access the configuration
    input_path = config_manager.get_input_path()
    output_path = config_manager.get_output_path()
    keep_split_card_images = config_manager.get_keep_split_card_images()
    crawl_directories = config_manager.get_crawl_directories()

    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_path}")
    print(f"Keep split card images: {keep_split_card_images}")
    print(f"Crawl subdirectories: {crawl_directories}")
    # The rest of your application logic would go here, using the configuration values
