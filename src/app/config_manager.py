import json
import json
from typing import Optional, Any, Dict
from .cli_args_parser import CLIArgsParser

AppConfig = Dict[str, Any]

class ConfigManager:
    """Manages application configuration settings.

    This class handles loading configuration settings from a JSON file and updating them
    with command-line arguments. Command-line arguments take precedence over settings
    from the configuration file.

    Attributes:
        config: A dictionary holding the configuration settings.
    """
    def __init__(self, config_file: str = "config.json") -> None:  # Removed cli_args from here
        """Initializes the ConfigManager.

        Loads settings from the specified JSON file and updates them with any provided
        command-line arguments.

        Args:
            config_file: The path to the JSON configuration file. Defaults to "config.json".

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        self.config: AppConfig = {}

        try:
            with open(config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Configuration file not found: {config_file}. Using default settings.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in configuration file: {e}", e.doc, e.pos)

        cli_args_parser = CLIArgsParser()  # Instantiate the CLIArgsParser
        cli_config = cli_args_parser.parse_arguments()  # Parse and map CLI arguments
        self.update_with_cli_args(cli_config)  # Update configuration with CLI arguments

    def update_with_cli_args(self, cli_config: AppConfig) -> None:  # Modified this to use cli_config
        """Updates the configuration with values from command-line arguments.

        Command-line arguments take precedence over settings loaded from the configuration file.

        Args:
            cli_config: A dictionary of command-line arguments mapped to configuration keys.  # Modified this docstring
        """
        for key, value in cli_config.items():
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
