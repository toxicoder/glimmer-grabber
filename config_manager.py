import json
from typing import Optional, Any

class ConfigManager:
    """
    Manages application configuration settings loaded from a JSON file.

    Attributes:
        config (dict): A dictionary holding the configuration settings.
    """
    def __init__(self, config_file: str = "config.json") -> None:
        """
        Initializes the ConfigManager by loading settings from the specified JSON file.

        Args:
            config_file (str): The path to the JSON configuration file. Defaults to "config.json".

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            json.JSONDecodeError: If the configuration file contains invalid JSON.
        """
        try:
            with open(config_file, "r") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in configuration file: {e}", e.doc, e.pos)

    def get_input_path(self) -> Optional[str]:
        """
        Retrieves the input path from the configuration.

        Returns:
            Optional[str]: The input path as a string, or None if not found.
        """
        return self.config.get("input_path")

    def get_output_path(self) -> Optional[str]:
        """
        Retrieves the output path from the configuration.

        Returns:
            Optional[str]: The output path as a string, or None if not found.
        """
        return self.config.get("output_path")

    def get_threshold(self) -> Optional[float]:
        """
        Retrieves the processing threshold from the configuration.

        Returns:
            Optional[float]: The threshold as a float, or None if not found.
        """
        return self.config.get("threshold")

    def get_api_key(self) -> Optional[str]:
        """
        Retrieves the API key from the configuration.

        Returns:
            Optional[str]: The API key as a string, or None if not found.
        """
        return self.config.get("api_key")
