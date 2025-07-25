import logging

def setup_logging() -> logging.Logger:
    """
    Sets up basic logging for the application.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)
