from config_manager import ConfigManager
from cli import parse_arguments

if __name__ == "__main__":
    args = parse_arguments()

    config_manager = ConfigManager(cli_args=args)

    # Now you can use config_manager to access the configuration
    input_path = config_manager.get_input_path()
    output_path = config_manager.get_output_path()
    keep_split_card_images = config_manager.get_keep_split_card_images()
    crawl_directories = config_manager.get_crawl_directories()

    print(f"Using input path: {input_path}")
    print(f"Using output path: {output_path}")
    print(f"Keep split card images: {keep_split_card_images}")
    print(f"Crawl subdirectories: {crawl_directories}")
    
    # Initialize history log
    history_file = os.path.join(output_path, "processed_images.txt")
    if not os.path.exists(history_file):
        with open(history_file, "w") as f:
            pass  # Create an empty file

    # The rest of your application logic would go here, using the configuration values
    from image_reader import read_images_from_folder
    import os

    image_files = read_images_from_folder()  # Assuming this returns a list of image file *paths*
    
    with open(history_file, "r") as f:
        processed_images = [line.strip() for line in f]

    with open(history_file, "a") as f:
        for image_path in image_files:
            image_name = os.path.basename(image_path) # Extract filename from path
            if image_name in processed_images:
                print(f"Skipping already processed image: {image_name}")
                continue
            
            # Process the image here (replace with actual processing logic)
            print(f"Processing image: {image_name}") 
            # Example: processed_image = process_image(image_path) 
            
            f.write(image_name + "\n")  # Append *filename* to history log
