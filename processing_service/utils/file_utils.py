import requests

def download_image(url: str) -> bytes:
    """
    Downloads an image from a URL and returns its content as bytes.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")
        return b""
