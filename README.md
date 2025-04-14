# Glimmer Grabber

**Glimmer Grabber** is a command-line tool designed to digitize collections of Lorcana Trading Cards. It processes images of card collections, segments individual cards using a YOLOv8 model, identifies card names with OCR, fetches detailed card data from an API, and generates a CSV file with the results. This tool is ideal for collectors who want to catalog their physical cards efficiently.

## Features

- **Image Processing**: Automatically preprocesses images to enhance quality and segments individual cards.
- **Card Segmentation**: Uses a YOLOv8 segmentation model to detect and isolate cards from collection images.
- **Card Identification**: Employs OCR (via Tesseract) to extract card names from segmented images.
- **Data Fetching**: Retrieves detailed card data from the Lorcana API, with local caching to minimize API calls.
- **CSV Output**: Generates a CSV file containing card details, saved to a user-specified directory.
- **Configurable Workflow**: Supports customization via a JSON configuration file and command-line arguments.

## Installation

Follow these steps to set up Glimmer Grabber on your system:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/toxicoder/glimmer-grabber.git
   cd glimmer-grabber
   ```

2. **Create a Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -e .
   ```
   This installs the project and its dependencies (e.g., NumPy, OpenCV, Ultralytics) as specified in `pyproject.toml`.

4. **Verify Installation** (Optional):
   Run the unit tests to ensure everything is set up correctly:
   ```bash
   python -m unittest discover -s tests
   ```

## Usage

Run Glimmer Grabber using the command-line interface:

```bash
glimmer-grabber [input_dir] [output_dir] [options]
```

### Positional Arguments

- **`input_dir`**: Directory containing images of Lorcana card collections (default: `"input"`).
- **`output_dir`**: Directory where the CSV file and optional segmented images are saved (default: `"output"`).

### Optional Arguments

- **`--keep_split_card_images`**: Retain intermediate split card images (default: `False`).
- **`--crawl_directories`**: Recursively search subdirectories in `input_dir` for images (default: `True`).
- **`--save_segmented_images`**: Save segmented card images to a specified directory (default: `False`).
- **`--save_segmented_images_path`**: Directory to save segmented images (default: `"segmented_images"` if unspecified).

### Example Commands

1. Basic usage with default settings:
   ```bash
   glimmer-grabber input_images output_data
   ```
   Processes images in `input_images` and saves a CSV to `output_data`.

2. Save segmented images:
   ```bash
   glimmer-grabber input_images output_data --save_segmented_images --save_segmented_images_path segmented_cards
   ```
   Saves segmented card images to `segmented_cards` in addition to the CSV.

3. Disable directory crawling:
   ```bash
   glimmer-grabber input_images output_data --crawl_directories=False
   ```
   Processes only top-level images in `input_images`.

## Configuration

Glimmer Grabber can be configured via a `config.json` file in the working directory. Command-line arguments override these settings where applicable.

### Example `config.json`

```json
{
    "input_path": "input",
    "output_path": "output",
    "keep_split_card_images": false,
    "crawl_directories": true,
    "save_segmented_images": false,
    "save_segmented_images_path": "segmented_images",
    "api_url": "https://lorcanajson.org/",
    "cache_duration": 3600
}
```

- **`input_path`**: Default input directory.
- **`output_path`**: Default output directory.
- **`keep_split_card_images`**: Whether to retain split images (not currently implemented).
- **`crawl_directories`**: Enable recursive image search.
- **`save_segmented_images`**: Save segmented images.
- **`save_segmented_images_path`**: Directory for segmented images.
- **`api_url`**: Lorcana API endpoint (default: `"https://lorcanajson.org/"`).
- **`cache_duration`**: Cache validity in seconds (default: `3600`, or 1 hour).

## How It Works

Here’s a detailed breakdown of Glimmer Grabber’s workflow:

1. **Command-Line Input**:
   - The user runs `glimmer-grabber` with arguments parsed by `cli_args_parser.py`.
   - `ConfigManager` merges settings from `config.json` and CLI arguments.

2. **Image Reading**:
   - Images are read from `input_dir` using `image_reader.py` (assumed implemented).
   - If `crawl_directories` is `True`, subdirectories are recursively searched.

3. **Image Preprocessing**:
   - `ImagePreprocessor` applies:
     - Noise reduction (e.g., median blur).
     - Illumination normalization (e.g., CLAHE).
     - Grayscale conversion.
   - Configurable via a preprocessing section in `config.json`.

4. **Card Segmentation**:
   - `CardSegmenter` uses a YOLOv8 segmentation model (`yolov8n-seg.pt`):
     - Detects cards and generates bounding boxes and masks.
     - Crops individual card images.
   - If `save_segmented_images` is `True`, saves images to `save_segmented_images_path`.

5. **Card Identification**:
   - OCR (via Tesseract) extracts card names from segmented images.
   - Preprocessing (e.g., CLAHE, thresholding) enhances OCR accuracy.

6. **Data Fetching**:
   - `CardDataFetcher` retrieves card data from the Lorcana API or a local cache (`card_data_cache.json`).
   - Cache is valid for `cache_duration` seconds; otherwise, it fetches fresh data.

7. **CSV Generation**:
   - A CSV file (e.g., `lorcana_collection_1.csv`) is created in `output_dir`.
   - Contains card details (e.g., name, type, set) fetched from the API.
   - Filename increments to avoid overwriting existing files.

## Output Format

The CSV file includes columns based on the API response (assumed fields):
- `name`: Card name identified by OCR.
- `type`: Card type (e.g., Character, Item).
- `set`: Card set (e.g., "The First Chapter").

Example:
```
name,type,set
"Ursula - Power Hungry",Character,"The First Chapter"
"Magic Broom - Bucket Brigade",Item,"The First Chapter"
```

## Requirements

- **Python**: 3.7 or higher.
- **Dependencies** (from `pyproject.toml`):
  - `numpy`: Numerical operations.
  - `opencv-python`: Image processing.
  - `scikit-image`: Additional image utilities.
  - `requests`: API calls.
  - `ultralytics`: YOLOv8 model.
  - `pytesseract`: OCR functionality (install separately if needed).

Install additional requirements:
```bash
pip install pytesseract
```

## Troubleshooting

- **No Cards Detected**: Ensure images are clear and well-lit; adjust preprocessing settings.
- **OCR Errors**: Improve image quality or refine OCR preprocessing in `card_segmenter.py`.
- **API Issues**: Verify `api_url` and internet connection; check cache validity.

## License

This project is licensed under the MIT License. See `LICENSE` for details.
