"""Retry decorator for handling retries."""
import time
import logging
import functools

def retry(max_retries=3, delay=5):
    """
    Retry decorator for handling retries.
    
    Args:
        max_retries (int): Maximum number of retries.
        delay (int): Delay between retries in seconds.
    
    Returns:
        function: Decorated function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logging.error(f"Maximum retries ({max_retries}) reached for {func.__name__}. Last error: {str(e)}")
                        raise
                    
                    logging.warning(f"Retry {retries}/{max_retries} for {func.__name__} due to: {str(e)}")
                    time.sleep(delay)
            
            raise Exception(f"Failed after {max_retries} retries")
        
        return wrapper
    
    return decorator
