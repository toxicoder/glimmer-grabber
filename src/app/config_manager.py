import json
from typing import Optional, Any, Dict
import argparse
import os
from src.app.cli_args_parser import CLIArgsParser

AppConfig = Dict[str, Any]

class ConfigManager:
    """Manages application configuration settings.

    This class handles loading configuration settings from a JSON file and updating them
    with command-line arguments. Command-line arguments take precedence over settings
    from the configuration file.

    Attributes:
        config: A dictionary holding the configuration settings.
    """

    def __init__(self, config_file: str = "config.json", cli_args: Optional[argparse.Namespace] = None) -> None:
        """Initializes the ConfigManager.

        Loads settings from the specified JSON file and updates them with any provided
        command-line arguments.

        Args:
            config_file: The path to the JSON configuration file. Defaults to "config.json".
            cli_args: Optional command-line arguments to override configuration file settings.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        self.config: AppConfig = {}

        config_path = os.path.abspath(config_file) # Use the config_file argument as a path relative to the project root.

        try:
            with open(config_path, "r") as f:
                file_config = json.load(f)
                if isinstance(file_config, dict):
                    self.config.update(file_config)
                else:
                    print(f"Invalid configuration format in {config_path}. Expected a JSON object.")
        except FileNotFoundError:
            print(f"Configuration file not found: {config_path}. Using default settings.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in configuration file: {e}", e.doc, e.pos)

        if cli_args:
            self.update_with_cli_args(cli_args)

    def update_with_cli_args(self, cli_args: argparse.Namespace) -> None:
        """Updates the configuration with values from command-line arguments.

        Command-line arguments take precedence over settings loaded from the configuration file.

        Args:
            cli_args: An argparse.Namespace object containing command-line arguments.
        """
        for key, value in vars(cli_args).items():
            if value is not None:
                self.config[key] = value

    def get_input_path(self) -> Optional[str]:
        """Retrieves the input path.

        Returns:
            The input path as a string, or None if not found.
        """
        return self.config.get("input_path")

    def get_output_path(self) -> Optional[str]:
        """Retrieves the output path.

        Returns:
            The output path as a string, or None if not found.
        """
        return self.config.get("output_path")

    def get_threshold(self) -> Optional[float]:
        """Retrieves the processing threshold.

        Returns:
            The threshold as a float, or None if not found.
        """
        return self.config.get("threshold")

    def get_api_key(self) -> Optional[str]:
        """Retrieves the API key.

        Returns:
            The API key as a string, or None if not found.
        """
        return self.config.get("api_key")

    def get_keep_split_card_images(self) -> Optional[bool]:
        """Retrieves the setting for keeping split card images.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("keep_split_card_images")

    def get_crawl_directories(self) -> Optional[bool]:
        """Retrieves the setting for crawling subdirectories.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("crawl_directories")

    def get_save_segmented_images_path(self) -> Optional[str]:
        """Retrieves the path for saving segmented card images.

        Returns:
            The path as a string, or None if not found.
        """
        return self.config.get("save_segmented_images_path")

    def get_save_segmented_images(self) -> Optional[bool]:
        """Retrieves the setting for saving segmented card images.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("save_segmented_images")
