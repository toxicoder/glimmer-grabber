import json
from typing import Optional, Any, Dict

AppConfig = Dict[str, Any]
CLIArgs = Optional[Dict[str, Any]]

class ConfigManager:
    """Manages application configuration settings loaded from a JSON file,
    prioritizing CLI arguments over the configuration file.

    Attributes:
        config: A dictionary holding the configuration settings.
        cli_args: A dictionary holding the CLI arguments.
    """
    def __init__(self, config_file: str = "config.json", cli_args: CLIArgs = None) -> None:
        """Initializes the ConfigManager by loading settings from the specified JSON file
        and updating them with CLI arguments.

        Args:
            config_file: The path to the JSON configuration file. Defaults to "config.json".
            cli_args: A dictionary of CLI arguments. Defaults to None.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        self.config: AppConfig = {}
        self.cli_args: AppConfig = {} if cli_args is None else cli_args

        try:
            with open(config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"Configuration file not found: {config_file}. Using default settings.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in configuration file: {e}", e.doc, e.pos)

        self.update_with_cli_args(self.cli_args)

    def update_with_cli_args(self, cli_args: AppConfig) -> None:
        """Updates the configuration with values from CLI arguments, giving them priority.

        Args:
            cli_args: A dictionary of CLI arguments.
        """
        # Map CLI argument names to config keys. Adjust as necessary to match your CLI arguments.
        arg_mapping: Dict[str, str] = {
            "input_dir": "input_path",
            "output_dir": "output_path",  # Assuming you might add this CLI argument later
            "threshold": "threshold",
            "api_key": "api_key",
            "keep_split_card_images": "keep_split_card_images",
            "crawl_directories": "crawl_directories",
            "save_segmented_images_path": "save_segmented_images_path",
            "save_segmented_images": "save_segmented_images"
        }

        for arg_name, config_key in arg_mapping.items():
            if arg_name in cli_args and cli_args[arg_name] is not None:
                self.config[config_key] = cli_args[arg_name]

    def get_input_path(self) -> Optional[str]:
        """Retrieves the input path, prioritizing CLI arguments over the configuration file.

        Returns:
            The input path as a string, or None if not found.
        """
        return self.config.get("input_path")

    def get_output_path(self) -> Optional[str]:
        """Retrieves the output path, prioritizing CLI arguments over the configuration file.

        Returns:
            The output path as a string, or None if not found.
        """
        return self.config.get("output_path")

    def get_threshold(self) -> Optional[float]:
        """Retrieves the processing threshold, prioritizing CLI arguments over the configuration file.

        Returns:
            The threshold as a float, or None if not found.
        """
        return self.config.get("threshold")

    def get_api_key(self) -> Optional[str]:
        """Retrieves the API key, prioritizing CLI arguments over the configuration file.

        Returns:
            The API key as a string, or None if not found.
        """
        return self.config.get("api_key")

    def get_keep_split_card_images(self) -> Optional[bool]:
        """Retrieves the keep_split_card_images setting, prioritizing CLI arguments over the configuration file.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("keep_split_card_images")

    def get_crawl_directories(self) -> Optional[bool]:
        """Retrieves the crawl_directories setting, prioritizing CLI arguments over the configuration file.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("crawl_directories")

    def get_save_segmented_images_path(self) -> Optional[str]:
        """Retrieves the path to save segmented card images, prioritizing CLI arguments over the configuration file.

        Returns:
            The path as a string, or None if not found.
        """
        return self.config.get("save_segmented_images_path")

    def get_save_segmented_images(self) -> Optional[bool]:
        """Retrieves the save_segmented_images setting, prioritizing CLI arguments over the configuration file.

        Returns:
            The setting as a bool, or None if not found.
        """
        return self.config.get("save_segmented_images")
