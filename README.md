# Glimmer Grabber

**Glimmer Grabber** is a command-line tool designed to digitize collections of Lorcana Trading Cards. It processes images of card collections, segments individual cards using a YOLOv8 model, identifies card names with OCR, fetches detailed card data from an API, and generates a CSV file with the results. This tool is ideal for collectors who want to catalog their physical cards efficiently.

## Features

- **Image Preprocessing**: Enhances input image quality through automated noise reduction, illumination normalization, and grayscale conversion.
- **Card Segmentation**: Employs a YOLOv8 model to accurately detect and isolate individual cards from images.
- **OCR-based Card Identification**: Extracts card names from segmented card images using Tesseract OCR.
- **Comprehensive Data Fetching**: Retrieves detailed card information from the Lorcana API, utilizing a local cache to optimize performance and reduce API calls.
- **CSV Export**: Generates a CSV file with the digitized card collection data, including details fetched from the API.
- **Flexible Configuration**: Allows customization of the workflow through a `config.json` file and command-line arguments.

## Installation

Follow these steps to set up Glimmer Grabber on your system:

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/toxicoder/glimmer-grabber.git
    cd glimmer-grabber
    ```

2.  **Create a Virtual Environment**:
    It's recommended to create a virtual environment to manage dependencies:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    # On Windows: `.venv\Scripts\activate`
    ```

3.  **Install Tesseract OCR Engine**:
    **Glimmer Grabber** uses Tesseract for OCR. You must install it on your system.
    *   **macOS**: `brew install tesseract`
    *   **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
    *   **Windows**: Download the installer from the [official Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/Installation.html). Ensure Tesseract is added to your system's PATH.

4.  **Install Python Dependencies**:
    Install the project and its Python dependencies, including `pytesseract` (the Python wrapper for Tesseract):
    ```bash
    pip install -e .
    ```
    This command reads the `pyproject.toml` file and installs all necessary packages (e.g., NumPy, OpenCV, Ultralytics, `pytesseract`).

5.  **Verify Installation** (Optional but Recommended):
    Run the unit tests to ensure everything is set up correctly:
    ```bash
    python -m unittest discover -s tests
    ```

## Usage

Run **Glimmer Grabber** using the command-line interface:

```bash
glimmer-grabber <input_dir> <output_dir> [options]
```

### Positional Arguments

-   **`<input_dir>`**: (Required) Path to the directory containing images of your Lorcana card collections. Referred to as `input_dir` in configuration and internal logic.
-   **`<output_dir>`**: (Required) Path to the directory where the output CSV file and any optional segmented images will be saved. Referred to as `output_dir` in configuration and internal logic.

*Note: While these arguments are required on the command line, their default values can be specified in a `config.json` file (e.g., `"input_path": "input"`, `"output_path": "output"`). If the `config.json` file is present and these keys are set, you can omit these arguments from the command line.*

### Optional Arguments

-   **`--keep_split_card_images`**: If specified, the tool will attempt to retain intermediate images created during card splitting. (Default: `False`. Note: This feature is not fully implemented functionally.)
-   **`--crawl_directories`**: Recursively search through subdirectories within the `<input_dir>` for images. (Default: `True`, meaning subdirectories are searched). Set to `--crawl_directories=False` to disable this.
-   **`--save_segmented_images`**: If specified, saves the individual segmented card images. (Default: `False`).
-   **`--save_segmented_images_path <path>`**: Specifies the directory to save the segmented card images. This is used only if `--save_segmented_images` is also specified. (Default: `"segmented_images"` relative to the working directory, if not provided).

### Example Commands
1. Basic usage (assuming `input_images` and `output_data` directories exist):
   ```bash
   glimmer-grabber input_images output_data
   ```
   Processes images in `input_images` and saves a CSV to `output_data`. (Here `input_images` and `output_data` are example values for `<input_dir>` and `<output_dir>` respectively).

2. Save segmented images:
   ```bash
   glimmer-grabber input_images output_data --save_segmented_images --save_segmented_images_path segmented_cards
   ```
   Saves segmented card images to the `segmented_cards` directory (an example value for `--save_segmented_images_path <path>`) in addition to the CSV.

3. Disable directory crawling:
   ```bash
   glimmer-grabber input_images output_data --crawl_directories=False
   ```
   Processes only top-level images in `input_images`.

## Configuration

**Glimmer Grabber** can be configured via a `config.json` file. The application looks for this file in the directory where the `glimmer-grabber` command is executed (i.e., the current working directory). Command-line arguments will always override settings specified in the `config.json` file.

### Example `config.json`
```json
{
    "input_path": "input_images_from_config",
    "output_path": "output_data_from_config",
    "keep_split_card_images": false,
    "crawl_directories": true,
    "save_segmented_images": false,
    "save_segmented_images_path": "segmented_images_from_config",
    "api_url": "https://lorcanajson.org/",
    "cache_duration": 3600
}
```
-   **`input_path`**: Default directory for input images (corresponds to `<input_dir>`). If provided, `<input_dir>` can be omitted from the command line.
-   **`output_path`**: Default directory for output CSV and images (corresponds to `<output_dir>`). If provided, `<output_dir>` can be omitted from the command line.
-   **`keep_split_card_images`**: Boolean. If `true`, the tool will attempt to retain intermediate images from the card splitting process. (Corresponds to `--keep_split_card_images`. Note: The underlying functionality for this option is not yet fully implemented.)
-   **`crawl_directories`**: Boolean. If `true` (default), recursively searches for images in subdirectories of `input_path`. (Corresponds to `--crawl_directories`.)
-   **`save_segmented_images`**: Boolean. If `true`, saves individual segmented card images. (Corresponds to `--save_segmented_images`.)
-   **`save_segmented_images_path`**: String. Specifies the directory to save segmented images if `save_segmented_images` is `true`. (Default: `"segmented_images"`. Corresponds to `--save_segmented_images_path <path>`.)
-   **`api_url`**: String. The base URL for the Lorcana API. (Default: `"https://lorcanajson.org/"`).
-   **`cache_duration`**: Integer. Duration in seconds for which the local API data cache is considered valid. (Default: `3600`, i.e., 1 hour).

## How It Works

Here’s a high-level overview of **Glimmer Grabber**’s workflow:

1.  **Initialization & Configuration**:
    *   The user executes `glimmer-grabber` from the command line.
    *   `cli_args_parser.py` processes command-line arguments.
    *   `ConfigManager` loads settings from `config.json` (if present in the working directory) and merges them with command-line arguments, giving precedence to the latter.
    *   The main workflow is orchestrated by `cli.py`.

2.  **Image Input**:
    *   `image_reader.py` reads images from the specified `input_dir`.
    *   If `crawl_directories` is enabled (default), it recursively searches subdirectories for common image formats (e.g., `.jpg`, `.jpeg`, `.png`).

3.  **Image Preprocessing**:
    *   The `ImagePreprocessor` module enhances images for better analysis:
        *   Applies noise reduction (e.g., median blur).
        *   Performs illumination normalization (e.g., CLAHE).
        *   Converts images to grayscale.
    *   These preprocessing steps might be configurable via `config.json` in future versions or by advanced code modification.

4.  **Card Segmentation**:
    *   `CardSegmenter` utilizes a YOLOv8 segmentation model (e.g., `yolov8n-seg.pt`) to:
        *   Detect individual cards within the preprocessed images.
        *   Generate bounding boxes and masks for each detected card.
        *   Crop out individual card images from the originals.
    *   If `save_segmented_images` is enabled, these cropped card images are saved to the directory specified by `save_segmented_images_path`.

5.  **Card Name Identification (OCR)**:
    *   The system uses Tesseract OCR to extract names from the segmented card images.
    *   Image preprocessing techniques (like additional CLAHE or thresholding) may be applied to improve OCR accuracy before Tesseract processing.

6.  **Data Enrichment (API & Caching)**:
    *   `CardDataFetcher` takes the OCR-extracted card names.
    *   It first checks a local cache (`card_data_cache.json`, typically in the working directory) for existing data to minimize API calls. The cache validity is determined by `cache_duration`.
    *   If data is not in the cache or is outdated, it fetches detailed card information (like card type, set, etc.) from the configured Lorcana API (defaulting to `https://lorcanajson.org/`).
    *   Fetched data is then saved to the `card_data_cache.json` for future use.

7.  **CSV Output Generation**:
    *   The collected and enriched data is compiled into a list.
    *   A CSV file is generated in the specified `output_dir`.
    *   The filename includes a timestamp (e.g., `lorcana_collection_YYYYMMDD_HHMMSS.csv`) to prevent overwriting previous exports.
    *   The CSV includes the OCR-extracted `card_name` and other details obtained from the API.

## Output Format

The output is a CSV file (e.g., `lorcana_collection_YYYYMMDD_HHMMSS.csv`) generated in the specified `output_dir`.

The CSV file contains a header row and subsequent rows for each successfully processed and identified card. The columns are primarily derived from the data fields returned by the Lorcana API, plus an additional field added by this tool:

-   **`card_name`**: This is the name of the card as extracted by the OCR process from your image. It's what **Glimmer Grabber** *thinks* the card is.
-   **API Fields (e.g., `name`, `type`, `set`, etc.)**: The remaining columns are dynamically generated based on the data retrieved from the Lorcana API. Common fields include:
    *   `name`: The official name of the card according to the API. This can be useful to compare against the OCR-extracted `card_name`.
    *   `type`: The card's type (e.g., "Character", "Item", "Action").
    *   `set`: The set the card belongs to (e.g., "The First Chapter", "Rise of the Floodborn").
    *   Other fields provided by the API (e.g., `cost`, `inkable`, `rarity`, `image_url`) will also be included as separate columns if available.

The exact list of API-derived columns can vary depending on the data provided by the Lorcana API endpoint. The script attempts to fetch and validate at least `name`, `type`, and `set` for each card entry from the API.

### Example CSV Output:

```csv
card_name,name,type,set,cost,inkable,rarity
Ursula - Power Hungry,Ursula - Power Hungry,Character,The First Chapter,3,True,Rare
Magic Broom - Buclet Brigad,Magic Broom - Bucket Brigade,Item,The First Chapter,1,True,Common
Simba - Future King,Simba - Future King,Character,The First Chapter,1,True,Common
```
*(Note: The `card_name` might have slight variations from the official `name` due to OCR accuracy.)*

## Requirements

To run **Glimmer Grabber**, you'll need the following:

-   **Python**: Version 3.7 or higher.
-   **Tesseract OCR Engine**: This is a system-level dependency. **Glimmer Grabber** uses Tesseract for card name identification. Please see the "Installation" section for instructions on how to install Tesseract OCR on your operating system.
-   **Python Dependencies**: These are listed in `pyproject.toml` and are installed automatically when you run `pip install -e .` (as described in the "Installation" section). Key dependencies include:
    *   `numpy`: For numerical operations.
    *   `opencv-python`: For image processing tasks.
    *   `scikit-image`: For additional image utilities.
    *   `requests`: For making API calls to fetch card data.
    *   `ultralytics`: For the YOLOv8 object segmentation model.
    *   `pytesseract`: The Python wrapper for the Tesseract OCR engine.

## Troubleshooting

If you encounter issues while running **Glimmer Grabber**, consider the following:

-   **No Cards Detected / Poor Segmentation**:
    *   Ensure your input images are clear, well-lit, and cards are reasonably separated.
    *   Try adjusting image preprocessing settings (if configurable options are available or by modifying the code for advanced users).
    *   The YOLOv8 model might struggle with very unusual card presentations or image quality.

-   **OCR Errors (Incorrect Card Names)**:
    *   Improve the quality of your input images (lighting, focus, resolution).
    *   The OCR process is sensitive to image quality. Ensure segmented cards are clear.
    *   For advanced users: OCR preprocessing steps are within `src/core/card_segmenter.py` or related modules and could potentially be tuned, but this requires Python and image processing knowledge.

-   **API Issues / No Data Fetched**:
    *   Verify your internet connection.
    *   Check that the `api_url` in your `config.json` (or the default) is correct and accessible.
    *   The API might be temporarily down or rate-limiting.
    *   Cached data (`card_data_cache.json`) might be stale. You can try deleting this file (it's usually in your working directory) to force a fresh API fetch.

-   **`config.json` Not Working**:
    *   Ensure your `config.json` file is in the same directory where you are running the `glimmer-grabber` command (your current working directory).
    *   Verify the JSON syntax in your `config.json` is correct. Online JSON validators can help.
    *   Remember that command-line arguments will override settings in `config.json`.

-   **Tesseract / OCR Not Working (e.g., "Tesseract not found" errors)**:
    *   Ensure Tesseract OCR engine is correctly installed on your system (see "Installation" section).
    *   For Windows users, make sure the Tesseract installation directory is added to your system's PATH environment variable.
    *   The `pytesseract` Python library must also be installed (handled by `pip install -e .` as per the "Installation" section).

-   **General Issues**:
    *   Ensure all Python dependencies are correctly installed by running `pip install -e .` in your virtual environment.
    *   Run the unit tests (`python -m unittest discover -s tests`) to check if core components are functioning as expected.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
