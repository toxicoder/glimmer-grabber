import argparse
import os
import csv
import logging
import datetime
from typing import List

# Application-specific imports
from src.app.config_manager import ConfigManager
from src.app.image_reader import read_images_from_folder
from src.core.image_processor import process_images
from src.app.card_data_fetcher import CardDataFetcher
from src.app.cli_args_parser import CLIArgsParser
from src.core.exceptions import ImageProcessingError
from src.app.exceptions import APIFetchError, CacheError, DataFormatError

# Module-level logger
logger = logging.getLogger(__name__)

def setup_logging(log_output_path: str, log_file_name: str) -> None:
    """
    Configures the root logger for the application.

    This function sets up logging to output messages to both the console
    and a specified log file within the log_output_path.
    The log directory is created if it doesn't already exist.

    Args:
        log_output_path (str): The directory path where the log file will be stored.
        log_file_name (str): The name of the log file.
    """
    # Define the full path for the log file
    log_file_path = os.path.join(log_output_path, log_file_name)

    # Ensure the directory for the log file exists
    # os.path.dirname will get the directory part of the path
    # If log_output_path is a directory and log_file_name is just a file name,
    # then os.path.dirname(log_file_path) will correctly be log_output_path.
    # If log_file_path might already include deeper subdirectories specified in log_file_name (unlikely for just a name),
    # this will still work.
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logger.info(f"Created log directory: {log_dir}") # Log this action, but logger might not be fully set up yet.
                                                       # This message will go to console if basicConfig hasn't run.

    # Configure basic logging settings
    logging.basicConfig(
        level=logging.INFO,  # Set the default logging level to INFO
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define log message format
        handlers=[
            logging.StreamHandler(),  # Handler for console output
            logging.FileHandler(log_file_path)  # Handler for file output
        ]
    )
    logger.info(f"Logging configured. Log file at: {log_file_path}")


def load_processed_images(history_file_path: str) -> List[str]:
    """
    Loads a list of already processed image identifiers from a history file.

    This is used to prevent reprocessing images that have been successfully
    processed in previous runs.

    Args:
        history_file_path (str): Path to the file containing the history of
                                 processed image identifiers (one per line).

    Returns:
        List[str]: A list of image identifiers. Returns an empty list if the
                   history file does not exist or an error occurs during reading.
    """
    if not os.path.exists(history_file_path):
        logger.info(f"History file not found at {history_file_path}, starting fresh. No images will be skipped based on history.")
        return []
    try:
        with open(history_file_path, "r") as f:
            processed_ids = [line.strip() for line in f if line.strip()] # Ensure no empty lines are processed
            logger.info(f"Successfully loaded {len(processed_ids)} entries from history file {history_file_path}.")
            return processed_ids
    except IOError as e:
        logger.error(f"Could not read history file {history_file_path}: {e}", exc_info=True)
        return [] # Return empty list on error to allow application to continue


def generate_csv(card_data: List[dict], output_path: str) -> None:
    """
    Generates a CSV file from the fetched card data.

    The CSV file is named with a timestamp to ensure uniqueness and is saved
    in the specified output directory.

    Args:
        card_data (List[dict]): A list of dictionaries, where each dictionary
                                represents a card's data.
        output_path (str): The directory path where the CSV file will be saved.
    """
    if not card_data:
        logger.info("No card data provided to generate_csv. Skipping CSV generation.")
        return

    # Generate a timestamped filename for the CSV
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file_name = f"lorcana_collection_{timestamp}.csv"
    csv_file_path = os.path.join(output_path, csv_file_name)

    try:
        # Create the output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            logger.info(f"Created output directory: {output_path}")

        # Write data to the CSV file
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csvfile:
            # Assume all dicts in card_data have the same keys, use the first item to get fieldnames
            fieldnames = list(card_data[0].keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()  # Write the header row
            writer.writerows(card_data)  # Write all card data rows
        logger.info(f"Card data successfully saved to {csv_file_path}")
    except IOError as e:
        logger.error(f"Failed to write CSV file to {csv_file_path}: {e}", exc_info=True)
    except Exception as e:
        # Catch any other unexpected errors during CSV generation
        logger.error(f"An unexpected error occurred during CSV generation for {csv_file_path}: {e}", exc_info=True)


def main() -> None:
    """
    Main entry point for the GlimmerGrabber application.

    This function orchestrates the entire process:
    1.  Parses command-line arguments provided by the user.
    2.  Sets up application-wide logging.
    3.  Initializes the `ConfigManager` to load and manage configuration settings
        from `config.json` and command-line arguments.
    4.  Retrieves and logs the active configuration settings.
    5.  Loads the history of previously processed images (if any) to avoid redundant work.
    6.  Reads image files from the specified input directory.
        (TODO: Implement filtering of already processed images).
    7.  Processes the images using `src.core.image_processor` to identify card details.
    8.  Fetches additional card data from an external API via `src.app.card_data_fetcher`.
    9.  Combines extracted and fetched data.
    10. Generates a CSV report of the collected card data.

    Exceptions during critical stages are caught and logged, allowing for graceful termination.
    """
    # 1. Parse command-line arguments
    cli_parser = CLIArgsParser()
    args: argparse.Namespace = cli_parser.parse_arguments()

    # Determine config_file path from CLI args if provided, else use default for ConfigManager
    config_file_arg = args.config_file if hasattr(args, 'config_file') and args.config_file else None

    # 2. Initialize ConfigManager early to get all config values, including log file name
    # Pass CLI args to ConfigManager so it can use them for initial setup if needed (e.g. config_file path)
    config_manager: ConfigManager = ConfigManager(config_file=config_file_arg, cli_args=args)

    # 3. Set up logging using configuration from ConfigManager
    # The definitive output_path is used for logs.
    # If output_path is not set (e.g. required arg missing and no default in config),
    # default to current directory for logging.
    log_output_dir = config_manager.get_output_path() or "."
    log_file_name = config_manager.get_log_file_name()
    setup_logging(log_output_dir, log_file_name)

    logger.info("GlimmerGrabber application started.")
    logger.info(f"Using configuration file: {os.path.abspath(config_manager.actual_config_file_path_used)}") # Log actual config path used
    
    try:
        # 4. Retrieve and log active configuration settings
        input_path: str = config_manager.get_input_path()
        output_path: str = config_manager.get_output_path() # Re-get in case it was None before for logging setup
        history_file_path: str = config_manager.get_history_file_path() # Now correctly uses output_path

        # Ensure output_path is set, as it's crucial for many operations
        if not output_path:
            logger.error("Output path is not configured. Please specify 'output_dir' via CLI or in config.json.")
            # It's possible that initial_log_dir was used for logging if output_path was None.
            # The application might not be able to proceed meaningfully without a defined output_path.
            raise ValueError("Output path is not configured, which is essential for application operation.")

        keep_split_card_images: bool = config_manager.get_keep_split_card_images()
        crawl_directories: bool = config_manager.get_crawl_directories()
        save_segmented_images: bool = config_manager.get_save_segmented_images()
        save_segmented_images_path: str = config_manager.get_save_segmented_images_path()

        # Retrieve new config values
        yolo_model_path = config_manager.get_yolo_model_path()
        api_url = config_manager.get_api_url()
        cache_duration = config_manager.get_cache_duration()
        segmentation_confidence = config_manager.get_segmentation_confidence_threshold()
        # image_preprocessing_settings = config_manager.get_image_preprocessing_settings() # Retrieved but used by ImagePreprocessor

        # 5. Log active configuration
        logger.info("--- Active Configuration ---")
        logger.info(f"  Input Path: {input_path or 'Not set'}")
        logger.info(f"  Output Path: {output_path or 'Not set - Using CWD for logs if needed'}")
        logger.info(f"  History File Path: {history_file_path}") # get_history_file_path now constructs full path
        logger.info(f"  Log File Name: {log_file_name} (in Output Path)")
        logger.info(f"  Keep Split Card Images: {keep_split_card_images}")
        logger.info(f"  Crawl Subdirectories: {crawl_directories}")
        logger.info(f"  Save Segmented Images: {save_segmented_images}")
        logger.info(f"  Save Segmented Images Path: {save_segmented_images_path or 'Not set'}")
        logger.info(f"  YOLO Model Path: {yolo_model_path}")
        logger.info(f"  API URL: {api_url}")
        logger.info(f"  Cache Duration: {cache_duration} seconds")
        logger.info(f"  Segmentation Confidence Threshold: {segmentation_confidence}")
        # logger.info(f"  Image Preprocessing Settings: {image_preprocessing_settings}") # Can be verbose
        logger.info("----------------------------")


        # 6. Load history of processed images
        processed_images_history: List[str] = load_processed_images(history_file_path)

        # 7. Read image files from the input directory
        # ConfigManager is instantiated inside read_images_from_folder, it will use the same config file logic
        image_files: List[str] = read_images_from_folder()

        logger.info(f"Found {len(image_files)} image file(s) in input directory '{input_path}'.")

        # Filter out images that are already in history (simple path match)
        # This is a basic filter. More robust would be checksums or relative paths from a common root.
        # For now, this assumes `image_files` and `processed_images_history` contain comparable paths/identifiers.
        unprocessed_image_files = [
            img_path for img_path in image_files
            if os.path.basename(img_path) not in processed_images_history # Example: Match by basename
        ]

        if len(unprocessed_image_files) < len(image_files):
            logger.info(f"Skipping {len(image_files) - len(unprocessed_image_files)} images already found in history.")

        if not unprocessed_image_files:
            logger.info("No new images to process after checking history.")
            return # Exit if no new images

        # 8. Process images
        # Pass relevant configuration to process_images
        # process_images will then pass relevant parts to CardSegmenter and run_inference
        # For instance, yolo_model_path and segmentation_confidence are now available in config_manager
        # CardSegmenter will get its model path from config_manager
        # run_inference will get its threshold from config_manager (passed via process_images)

        # process_images needs access to ConfigManager or specific values from it.
        # For now, let's modify process_images to accept config_manager.
        # This is a significant change to process_images signature.
        # A less invasive way is to have main() pass specific values.

        # Let's pass specific values to process_images for now.
        # process_images will need to be updated to accept confidence_threshold.
        # CardSegmenter will be updated to take its model path from ConfigManager.
        # ImagePreprocessor will be updated to take its settings from ConfigManager.

        # The `process_images` function needs to be adapted to use the new config,
        # or these values need to be passed to it.
        # For now, assuming CardSegmenter and ImagePreprocessor will be directly
        # instantiated with values from ConfigManager where they are used (e.g. inside process_images).
        # This requires process_images to either take config_manager or specific settings.

        # Simplest change for now: `process_images` remains, and components it calls
        # will be refactored to use their own ConfigManager instance or be passed specific settings.
        # `CardSegmenter` and `CardDataFetcher` will be updated to use `ConfigManager` internally
        # if one isn't passed, or use the one passed.
        # The current `process_images` doesn't instantiate these, so they do it themselves.

        processed_data = process_images(
            unprocessed_image_files,
            output_path, # For saving segmented images if enabled by CardSegmenter's config
            config_manager.get_save_segmented_images(), # from main config
            config_manager.get_save_segmented_images_path(), # from main config
            config_manager # Pass the main config_manager instance
        )
        logger.info(f"Successfully processed {len(processed_data)} new images.")

        # 9. Extract card names from processed data for fetching
        card_names: List[str] = []
        for data_item in processed_data:
            if data_item.get("segmentations"):
                for segmentation in data_item["segmentations"]:
                    if "name" in segmentation:
                        card_names.append(segmentation["name"])

        if not card_names:
            logger.info("No card names were extracted from the processed images. Nothing to fetch.")
            return

        logger.info(f"Extracted {len(card_names)} card names for data fetching.")

        # 10. Fetch additional card data using CardDataFetcher
        # CardDataFetcher will now use ConfigManager for its settings (api_url, cache_duration, cache_file_name)
        # The full cache_file_path is still best constructed here using output_path.
        cache_file_name = config_manager.get_cache_file_name()
        fetcher_cache_file_path = os.path.join(output_path, cache_file_name)

        card_data_fetcher: CardDataFetcher = CardDataFetcher(
            # Pass config_manager so it uses centrally managed settings
            config_manager=config_manager,
            # Explicitly set cache_file path based on output_dir, overriding potential default from config
            cache_file=fetcher_cache_file_path
        )
        fetched_card_data: List[dict] = card_data_fetcher.fetch_card_data(card_names)

        # The fetched_card_data might not perfectly align one-to-one with card_names if API has issues or names are ambiguous.
        # The following loop attempts to merge/associate them.

        final_data_for_csv = []
        # Iterate through originally extracted card_names to maintain some order/completeness.
        for extracted_name in card_names:
            # Attempt to find a match in the data fetched from the API.
            # This assumes the 'name' field in `fetched_card_data` corresponds to `extracted_name`.
            # This is a simple match; more complex scenarios might need fuzzy matching or multiple results handling.
            matched_api_card = next((cd for cd in fetched_card_data if cd.get("name") == extracted_name), None)

            if matched_api_card:
                # If a match is found, create a new dictionary for the CSV row.
                # Copy matched_api_card to avoid modifying it if it's reused.
                csv_entry = matched_api_card.copy()
                # Add the originally extracted name, useful if API name differs slightly or for reference.
                csv_entry["extracted_card_name"] = extracted_name
                final_data_for_csv.append(csv_entry)
            else:
                # If no match found in API data, log it and optionally add a placeholder.
                logger.warning(f"Could not find fetched API data for extracted card name: {extracted_name}")
                # Example placeholder:
                # final_data_for_csv.append({"extracted_card_name": extracted_name, "api_status": "not_found"})

        # 11. Generate CSV from the combined data
        if final_data_for_csv:
            generate_csv(final_data_for_csv, output_path)
        else:
            logger.info("No final card data available to save to CSV.")

    except (FileNotFoundError, ImageProcessingError, APIFetchError, CacheError, DataFormatError) as e:
        # Handle known, specific exceptions from the application logic
        logger.error(f"A critical application error occurred: {e}", exc_info=True)
    except Exception as e:
        # Handle any other unexpected exceptions
        logger.exception("An unexpected critical error occurred in the main application flow:")
    finally:
        logger.info("GlimmerGrabber application finished.")


if __name__ == "__main__":
    # This ensures main() is called only when the script is executed directly
    main()
