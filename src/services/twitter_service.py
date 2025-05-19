"""Twitter service for posting tweets."""
import logging
import time
import tweepy
from ..config.config import X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET, MAX_RETRIES, RETRY_DELAY
from ..utils.retry import retry

class TwitterService:
    """Service for interacting with X (Twitter) API."""
    
    def __init__(self, api_key=X_API_KEY, api_secret=X_API_SECRET, 
                 access_token=X_ACCESS_TOKEN, access_token_secret=X_ACCESS_TOKEN_SECRET):
        """Initialize the TwitterService."""
        self.auth = tweepy.OAuth1UserHandler(
            api_key,
            api_secret,
            access_token,
            access_token_secret
        )
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        logging.info("Twitter service initialized")
    
    @retry(max_retries=MAX_RETRIES, delay=RETRY_DELAY)
    def post_tweet(self, text):
        """Post a tweet with the given text."""
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data['id']
            logging.info(f"Successfully posted tweet with ID {tweet_id}")
            return tweet_id
        except AttributeError:
            status = self.api.update_status(text)
            logging.info(f"Successfully posted tweet with ID {status.id}")
            return status.id
        except tweepy.TweepyException as e:
            if hasattr(e, 'api_codes') and 429 in e.api_codes:
                logging.warning("Rate limit exceeded, sleeping and retrying...")
                time.sleep(60)  # Sleep for a minute
                raise  # Re-raise for the retry decorator to handle
            else:
                logging.error(f"Failed to post tweet: {str(e)}")
                raise
