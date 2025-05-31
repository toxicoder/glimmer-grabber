# src/app/exceptions.py

class APIFetchError(Exception):
    """
    Custom exception raised for errors encountered during API data fetching.

    This exception typically indicates issues with network connectivity,
    API server errors (e.g., 5xx status codes), timeouts, or other problems
    preventing successful data retrieval from an external API.

    Attributes:
        message (str): A human-readable message describing the error.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class CacheError(Exception):
    """
    Custom exception raised for errors related to caching operations.

    This can include issues such as failing to read from or write to the cache file,
    I/O errors during cache operations, or problems with cache file permissions.

    Attributes:
        message (str): A human-readable message describing the cache error.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class DataFormatError(Exception):
    """
    Custom exception raised for errors related to invalid data formats.

    This exception is used when data read from an external source (like an API
    or a cache file) does not conform to the expected structure or type.
    For example, expecting a list but receiving a dictionary, or missing
    required fields in data entries.

    Attributes:
        message (str): A human-readable message describing the data format error.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
