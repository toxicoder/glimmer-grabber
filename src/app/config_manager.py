# Standard library imports
import json
import logging
import os
from typing import Any, Dict, Optional, Tuple # Added Tuple
import argparse # argparse is used for type hinting cli_args

# Type alias for application configuration dictionary
AppConfig = Dict[str, Any]

# Module-level logger
logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages application configuration settings.

    This class is responsible for loading configuration settings from a JSON file
    (e.g., `config.json`) and allowing these settings to be overridden by
    command-line arguments. The precedence is: CLI arguments > config file settings > default values defined here.
    It provides getter methods to access various configuration parameters
    throughout the application.

    Attributes:
        config (AppConfig): A dictionary holding the merged configuration settings
                            from the config file and CLI arguments.
    """

    # Define default values for various settings
    DEFAULT_CONFIG_FILE = "config.json"
    DEFAULT_API_URL = "https://lorcanajson.org/"
    DEFAULT_CACHE_FILE_NAME = "card_data_cache.json"
    DEFAULT_CACHE_DURATION = 3600  # 1 hour
    DEFAULT_YOLO_MODEL_PATH = "yolov8n-seg.pt"
    DEFAULT_LOG_FILE_NAME = "glimmer_grabber.log"
    DEFAULT_HISTORY_FILE_NAME = "processed_images.log" # Default name, path is constructed
    DEFAULT_SEGMENTATION_CONFIDENCE_THRESHOLD = 0.5
    DEFAULT_IMAGE_PREPROCESSING_SETTINGS = {
        "contrast_check_threshold": 0.35,
        "illumination_clip_limit": 2.0,
        "illumination_tile_grid_size": (8, 8), # Tuple
        "noise_strength": 10,
        "noise_color_strength": 10,
        "noise_template_window_size": 7,
        "noise_search_window_size": 21,
    }


    def __init__(self, config_file: Optional[str] = None, cli_args: Optional[argparse.Namespace] = None) -> None:
        """
        Initializes the ConfigManager by loading settings and merging CLI arguments.
        ... (rest of docstring remains similar)
        Args:
            config_file (Optional[str]): The path to the JSON configuration file.
                               If None, defaults to "config.json" in the current working directory.
            cli_args (Optional[argparse.Namespace]): An object (typically from `argparse`)
                                                     containing command-line arguments.
        """
        self.config: AppConfig = {}
        actual_config_file = config_file if config_file is not None else self.DEFAULT_CONFIG_FILE
        logger.debug(f"Initializing ConfigManager with config file: '{actual_config_file}' and CLI args: {cli_args}")

        config_path = os.path.abspath(actual_config_file)
        logger.info(f"Attempting to load configuration from: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                if isinstance(file_config, dict):
                    self.config.update(file_config)
                    logger.info(f"Successfully loaded and applied configuration from {config_path}.")
                else:
                    logger.warning(f"Invalid configuration format in '{config_path}'. Expected a JSON object (dict), "
                                   f"got {type(file_config)}. Proceeding with defaults/CLI args.")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: '{config_path}'. "
                           "Using default settings and/or CLI arguments if provided.")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in configuration file '{config_path}': {e}", exc_info=True)

        if cli_args:
            logger.debug(f"Updating configuration with CLI arguments: {vars(cli_args)}")
            self.update_with_cli_args(cli_args)

        logger.debug(f"Final configuration state after initialization: {self.config}")

    def update_with_cli_args(self, cli_args: argparse.Namespace) -> None:
        """
        Updates the current configuration with values from command-line arguments.
        ... (rest of docstring remains similar)
        """
        updated_keys = []
        for key, value in vars(cli_args).items():
            # Only override if the CLI arg was actually provided (value is not None)
            # And for boolean flags, action="store_true" defaults to False if not present,
            # so we need to check if it's True or if it's a non-boolean that's not None.
            is_boolean_flag_true = isinstance(value, bool) and value is True
            is_non_boolean_provided = not isinstance(value, bool) and value is not None

            if is_boolean_flag_true or is_non_boolean_provided:
                # For boolean flags set by 'action="store_true"', if the flag is present, 'value' is True.
                # If it's not present, 'value' is False (its default). We only want to override
                # if the flag was explicitly set. However, argparse handles this well; if a default
                # is True (like crawl_directories) and the user doesn't specify it, it remains True.
                # The critical part is that `value is not None` handles optional args that are not flags.
                # For flags, their value is always either True or False after parsing.

                # We update if the key is in our defined arg_mapping (from CLIArgsParser)
                # or if it's a general config option that might be passed via a hypothetical --config-key style arg
                # For now, assuming cli_args keys directly match or are mapped by CLIArgsParser to self.config keys.

                if self.config.get(key) != value:
                    logger.info(f"Overriding configuration key '{key}' with CLI argument. "
                                f"New value: '{value}', Previous value: '{self.config.get(key)}'.")
                self.config[key] = value
                updated_keys.append(key)

        if updated_keys:
            logger.debug(f"Configuration updated with CLI arguments for keys: {updated_keys}.")
        else:
            logger.debug("No CLI arguments provided values that differed from existing config or defaults.")

    def get_input_path(self) -> Optional[str]:
        value = self.config.get("input_path")
        logger.debug(f"Retrieved 'input_path': {value}")
        return value

    def get_output_path(self) -> Optional[str]:
        value = self.config.get("output_path")
        logger.debug(f"Retrieved 'output_path': {value}")
        return value

    def get_threshold(self) -> Optional[float]: # Example, not currently used by many components directly
        value = self.config.get("threshold")
        logger.debug(f"Retrieved 'threshold': {value}")
        return value

    def get_api_key(self) -> Optional[str]:
        value = self.config.get("api_key")
        logger.debug(f"Retrieved 'api_key': {'********' if value else None}")
        return value

    def get_api_url(self) -> str:
        value = self.config.get("api_url", self.DEFAULT_API_URL)
        logger.debug(f"Retrieved 'api_url': {value}")
        return value

    def get_cache_file_name(self) -> str:
        # Note: Full cache_file_path is constructed in cli.py using output_path.
        # This getter is for the default name if CardDataFetcher were used standalone.
        value = self.config.get("cache_file_name", self.DEFAULT_CACHE_FILE_NAME)
        logger.debug(f"Retrieved 'cache_file_name': {value}")
        return value

    def get_cache_duration(self) -> int:
        value = self.config.get("cache_duration", self.DEFAULT_CACHE_DURATION)
        logger.debug(f"Retrieved 'cache_duration': {value}")
        return value

    def get_yolo_model_path(self) -> str:
        value = self.config.get("yolo_model_path", self.DEFAULT_YOLO_MODEL_PATH)
        logger.debug(f"Retrieved 'yolo_model_path': {value}")
        return value

    def get_log_file_name(self) -> str:
        # Full log_file_path is constructed in cli.py using output_path.
        value = self.config.get("log_file_name", self.DEFAULT_LOG_FILE_NAME)
        logger.debug(f"Retrieved 'log_file_name': {value}")
        return value

    def get_history_file_path(self) -> str:
        # This method constructs the full path, using output_path if available,
        # or defaults to a path relative to CWD if output_path is not set.
        output_dir = self.get_output_path()
        default_history_file_name = self.config.get("history_file_name", self.DEFAULT_HISTORY_FILE_NAME)

        if output_dir:
            # If output_path is set, history file is relative to it.
            default_path = os.path.join(output_dir, "data", default_history_file_name)
        else:
            # If output_path is not set (e.g. CLI only provided input_dir, or config.json is minimal)
            # default to "data/" subdirectory in CWD.
            default_path = os.path.join("data", default_history_file_name)

        # CLI provided history_file_path takes highest precedence
        value = self.config.get("history_file_path", default_path)
        logger.debug(f"Retrieved 'history_file_path': {value} (defaulted to '{default_path}' if not specified)")
        # Ensure the directory for the history file exists if we are returning a path
        if value: # value could be None if no default and no config
             os.makedirs(os.path.dirname(value), exist_ok=True)
        return value


    def get_segmentation_confidence_threshold(self) -> float:
        value = self.config.get("segmentation_confidence_threshold", self.DEFAULT_SEGMENTATION_CONFIDENCE_THRESHOLD)
        logger.debug(f"Retrieved 'segmentation_confidence_threshold': {value}")
        return value

    def get_image_preprocessing_settings(self) -> Dict[str, Any]:
        # Returns the entire sub-dictionary for preprocessing settings.
        # Individual components (like ImagePreprocessor) will parse this.
        value = self.config.get("image_preprocessing_settings", self.DEFAULT_IMAGE_PREPROCESSING_SETTINGS.copy())
        logger.debug(f"Retrieved 'image_preprocessing_settings': {value}")
        return value

    def get_keep_split_card_images(self) -> bool:
        value = self.config.get("keep_split_card_images", False)
        logger.debug(f"Retrieved 'keep_split_card_images': {value}")
        return value

    def get_crawl_directories(self) -> bool:
        value = self.config.get("crawl_directories", True)
        logger.debug(f"Retrieved 'crawl_directories': {value}")
        return value

    def get_save_segmented_images_path(self) -> Optional[str]:
        # This path should ideally be relative to output_path or an absolute path.
        # If not set, CardSegmenter might use a default sub-folder in output_path.
        value = self.config.get("save_segmented_images_path")
        logger.debug(f"Retrieved 'save_segmented_images_path': {value}")
        return value

    def get_save_segmented_images(self) -> bool:
        value = self.config.get("save_segmented_images", False)
        logger.debug(f"Retrieved 'save_segmented_images': {value}")
        return value
