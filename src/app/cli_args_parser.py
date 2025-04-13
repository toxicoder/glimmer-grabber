import argparse
from typing import Dict, Any

AppConfig = Dict[str, Any]

class CLIArgsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="CLI for processing card images.")
        self.parser.add_argument("input_dir", help="Path to the input directory.")
        self.parser.add_argument("output_dir", help="Path to the output directory.")
        self.parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
        self.parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")
        self.parser.add_argument("--save_segmented_images", action="store_true", help="Save segmented card images.")
        self.parser.add_argument("--save_segmented_images_path", help="Path to save segmented card images.")

        # Mapping of CLI arguments to configuration keys
        self.arg_mapping: Dict[str, str] = {
            "input_dir": "input_path",
            "output_dir": "output_path",
            "keep_split_card_images": "keep_split_card_images",
            "crawl_directories": "crawl_directories",
            "save_segmented_images_path": "save_segmented_images_path",
            "save_segmented_images": "save_segmented_images"
        }

    def parse_arguments(self) -> AppConfig:
        args = self.parser.parse_args()
        return self.map_arguments_to_config(args)

    def map_arguments_to_config(self, args: argparse.Namespace) -> AppConfig:
        config: AppConfig = {}
        for arg_name, config_key in self.arg_mapping.items():
            if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
                config[config_key] = getattr(args, arg_name)
        return config
