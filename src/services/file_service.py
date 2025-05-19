"""File service for saving post content locally."""
import os
import logging
from datetime import datetime
from ..config.config import MAX_RETRIES, RETRY_DELAY
from ..utils.retry import retry

class FileService:
    """Service for saving post content to local files."""
    
    def __init__(self, output_dir=None):
        """Initialize the FileService."""
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info(f"File service initialized with output directory: {self.output_dir}")
    
    @retry(max_retries=MAX_RETRIES, delay=RETRY_DELAY)
    def save_post(self, text):
        """Save post content to a local file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"post_{timestamp}.txt"
            filepath = os.path.join(self.output_dir, filename)
            
            with open(filepath, "w") as f:
                f.write(text)
            
            logging.info(f"Successfully saved post content to {filepath}")
            return filepath
        except Exception as e:
            logging.error(f"Failed to save post content: {str(e)}")
            raise
