import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="CLI for processing card images.")
    parser.add_argument("input_dir", help="Path to the input directory.")
    parser.add_argument("output_dir", help="Path to the output directory.")
    parser.add_argument("--keep_split_card_images", action="store_true", help="Keep split card images.")
    parser.add_argument("--crawl_directories", action="store_true", default=True, help="Crawl directories for images.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    print(args)
