# Standard library imports
import argparse
from typing import Dict, Any, Optional # Optional can be used if some args might not be present

# Type alias for the application's configuration dictionary structure
AppConfig = Dict[str, Any]

class CLIArgsParser:
    """
    Parses and manages command-line arguments for the GlimmerGrabber application.

    This class utilizes the `argparse` module to define, parse, and manage
    command-line arguments. It defines both positional and optional arguments
    that control various aspects of the application's behavior, such as input/output
    directories, image processing options, and paths for auxiliary files.

    The parsed arguments are then transformed into a more generic `AppConfig`
    dictionary, which is used by the `ConfigManager` to consolidate settings
    from both CLI and a configuration file.

    Attributes:
        parser (argparse.ArgumentParser): The main parser instance from the `argparse` module.
        arg_mapping (Dict[str, str]): A mapping from command-line argument names
                                      (as defined in `add_argument`) to the keys
                                      used in the `AppConfig` dictionary. This facilitates
                                      the transformation of parsed arguments into the
                                      application's configuration structure.
    """
    def __init__(self) -> None:
        """
        Initializes the CLIArgsParser and defines all expected command-line arguments.

        Sets up an `ArgumentParser` with a description of the CLI tool.
        It then adds all necessary arguments:
        - Positional: `input_dir`, `output_dir`.
        - Optional: Flags and valued options for features like keeping split images,
          controlling directory crawling, saving segmented images, and specifying
          paths for history or segmented image storage.

        A mapping (`self.arg_mapping`) is also defined to bridge the `argparse`
        argument names to the keys used internally by `ConfigManager`.
        """
        # Initialize the ArgumentParser with a description for the CLI
        self.parser = argparse.ArgumentParser(
            description="GlimmerGrabber: A CLI tool for processing Lorcana card images, "
                        "extracting data, and generating a collection CSV."
        )

        # --- Positional Arguments ---
        # These are required arguments that the user must provide in order.
        self.parser.add_argument(
            "input_dir",
            help="Path to the directory containing input images to be processed."
        )
        self.parser.add_argument(
            "output_dir",
            help="Path to the directory where output files (CSV, logs, cached data) will be saved."
        )

        # --- Optional Arguments ---
        # These arguments are not required and are typically prefixed with '--'.
        self.parser.add_argument(
            "--keep_split_card_images",
            action="store_true", # Makes this a boolean flag; present means True
            help="If set, keeps intermediate images generated during card splitting/segmentation."
        )
        self.parser.add_argument(
            "--crawl_directories",
            action="store_true",
            default=True, # Default behavior is to crawl subdirectories
            help="If set, recursively crawls subdirectories within the input_dir for images. Default is True."
        )
        self.parser.add_argument(
            "--save_segmented_images",
            action="store_true",
            help="If set, saves the segmented card images to a specified directory."
        )
        self.parser.add_argument(
            "--save_segmented_images_path",
            type=str, # Expects a string value (path)
            help="Directory path where segmented card images should be saved. "
                 "Used if --save_segmented_images is set."
        )
        self.parser.add_argument(
            "--history_file_path",
            type=str,
            help="Path to the history file that logs processed images. "
                 "Overrides 'history_file_name' in config.json if an absolute path is given, "
                 "otherwise, it's relative to output_dir/data/."
        )
        self.parser.add_argument(
            "--config_file", # Added to allow specifying config file via CLI
            type=str,
            help="Path to a custom JSON configuration file. Defaults to 'config.json' in CWD."
        )
        self.parser.add_argument(
            "--yolo_model_path",
            type=str,
            help="Path to the YOLOv8 segmentation model file (e.g., 'yolov8n-seg.pt')."
        )
        self.parser.add_argument(
            "--api_url",
            type=str,
            help="URL of the API endpoint to fetch card data from."
        )
        self.parser.add_argument(
            "--cache_duration",
            type=int, # Expects an integer value (seconds)
            help="Cache validity duration in seconds for API data."
        )
        self.parser.add_argument(
            "--segmentation_confidence_threshold",
            type=float, # Expects a float value (0.0 to 1.0)
            help="Confidence threshold for card segmentation."
        )
        # Note: image_preprocessing_settings are complex and better suited for config.json
        # than individual CLI args. Similarly for log_file_name (part of output_dir)
        # and cache_file_name (part of output_dir).

        # Mapping of command-line argument names (dest) to configuration keys used in AppConfig
        self.arg_mapping: Dict[str, str] = {
            "input_dir": "input_path",
            "output_dir": "output_path",
            "history_file_path": "history_file_path", # User can override full path
            "keep_split_card_images": "keep_split_card_images",
            "crawl_directories": "crawl_directories",
            "save_segmented_images_path": "save_segmented_images_path",
            "save_segmented_images": "save_segmented_images",
            "config_file": "config_file", # For ConfigManager to potentially use a different file
            "yolo_model_path": "yolo_model_path",
            "api_url": "api_url",
            "cache_duration": "cache_duration",
            "segmentation_confidence_threshold": "segmentation_confidence_threshold",
        }

    def parse_arguments(self) -> argparse.Namespace:
        """
        Parses the command-line arguments provided when the script is run.

        This method invokes the `parse_args()` method of the `ArgumentParser`
        instance, which processes the arguments from `sys.argv` (or a provided list).

        Returns:
            argparse.Namespace: An object where each command-line argument is an attribute.
                                For example, if an argument `--input_dir /path` is parsed,
                                `args.input_dir` will hold `/path`.
        """
        # The parse_args() method processes the arguments from sys.argv by default.
        args = self.parser.parse_args()
        # At this point, `args` is a Namespace object. For example, args.input_dir would hold the value.
        # No need to call map_arguments_to_config here, ConfigManager will handle it.
        return args

    def map_arguments_to_config(self, args: argparse.Namespace) -> AppConfig:
        """
        Maps parsed command-line arguments from an `argparse.Namespace` object
        to an `AppConfig` dictionary.

        This method iterates through the `arg_mapping` dictionary. For each defined
        mapping, it checks if the corresponding argument exists in the `args`
        Namespace and if its value is not None. If both conditions are met,
        the argument's value is added to the `AppConfig` dictionary using the
        mapped configuration key.

        This intermediate dictionary is then typically passed to `ConfigManager`
        to be merged with settings from a configuration file.

        Args:
            args (argparse.Namespace): The Namespace object returned by `parser.parse_args()`,
                                       containing the parsed command-line arguments as attributes.

        Returns:
            AppConfig: A dictionary where keys are the application's internal configuration
                       parameter names (e.g., "input_path") and values are the corresponding
                       values provided via command-line arguments. Only arguments that were
                       actually provided (not None) are included.
        """
        config: AppConfig = {} # Initialize an empty dictionary for the configuration
        # Iterate over the predefined mapping of CLI argument names to config keys
        for arg_name_in_namespace, config_key_in_appconfig in self.arg_mapping.items():
            # Check if the argument exists as an attribute in the parsed args object
            if hasattr(args, arg_name_in_namespace):
                value = getattr(args, arg_name_in_namespace)
                # Only include the argument in the config if its value is not None
                # This ensures that default values from argparse (if any) are included,
                # but arguments not provided by the user (which are often None for optional args)
                # are not explicitly set in this initial config dict. ConfigManager handles defaults later.
                if value is not None:
                    config[config_key_in_appconfig] = value
        return config
