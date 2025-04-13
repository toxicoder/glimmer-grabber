import argparse
from typing import Dict, Any

AppConfig = Dict[str, Any]

class CLIArgsParser:
    """Parses command-line arguments for the application.

    This class uses the `argparse` module to define and parse the command-line arguments
    required by the application. It also maps these arguments to a configuration dictionary
    for easier access and management of settings.
    """
    def __init__(self):
        """Initializes the CLIArgsParser and defines the command-line arguments."""
        self.parser = argparse.ArgumentParser(description="CLI for processing card images.")
        # Positional arguments
        self.parser.add_argument("input_dir", help="Path to the input directory.")
        self.parser.add_argument("output_dir", help="Path to the output directory.")
        # Optional arguments
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
        """Parses the command-line arguments.

        Returns:
            A dictionary containing the parsed arguments, mapped to their corresponding
            configuration keys.
        """
        args = self.parser.parse_args()
        return self.map_arguments_to_config(args)

    def map_arguments_to_config(self, args: argparse.Namespace) -> AppConfig:
        """Maps parsed command-line arguments to a configuration dictionary.

        Args:
            args: An argparse.Namespace object containing the parsed arguments.

        Returns:
            A dictionary where keys are configuration settings and values are the
            corresponding values from the command-line arguments.
        """
        config: AppConfig = {}
        for arg_name, config_key in self.arg_mapping.items():
            if hasattr(args, arg_name) and getattr(args, arg_name) is not None:
                config[config_key] = getattr(args, arg_name)
        return config
