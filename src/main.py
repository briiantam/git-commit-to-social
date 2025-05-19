"""Main application module."""
import os
import sys
import logging
import signal
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.config import get_hkt_time
from src.utils.logger import setup_logging
from src.utils.scheduler import Scheduler
from src.models.database import initialize_db, get_todays_commits, store_summary, mark_summary_as_posted, mark_commits_as_summarized
from src.services.git_service import GitService
from src.services.openai_service import OpenAIService
from src.services.twitter_service import TwitterService

setup_logging()

git_service = None
openai_service = None
twitter_service = None
scheduler = None

def initialize_services():
    """Initialize all services."""
    global git_service, openai_service, twitter_service, scheduler
    
    initialize_db()
    
    git_service = GitService()
    openai_service = OpenAIService()
    twitter_service = TwitterService()
    
    scheduler = Scheduler()

def generate_and_post_summary():
    """Generate a summary of today's commits and post it to X."""
    try:
        logging.info("Starting daily summary generation")
        
        git_service.process_new_commits()
        
        commits = get_todays_commits()
        
        if not commits:
            logging.info("No commits found for today")
            return
        
        summary = openai_service.summarize_commits(commits)
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary_id = store_summary(today, summary, len(commits))
        
        tweet_text = f"Daily commit summary ({today}):\n\n{summary}"
        twitter_service.post_tweet(tweet_text)
        
        mark_summary_as_posted(summary_id)
        mark_commits_as_summarized([commit["id"] for commit in commits])
        
        logging.info("Daily summary generated and posted successfully")
    except Exception as e:
        logging.error(f"Failed to generate and post summary: {str(e)}")

def monitor_commits():
    """Monitor for new commits and process them."""
    try:
        commit_count = git_service.process_new_commits()
        logging.info(f"Processed {commit_count} new commits")
    except Exception as e:
        logging.error(f"Failed to monitor commits: {str(e)}")

def handle_signal(signum, frame):
    """Handle signals to gracefully shutdown the application."""
    logging.info(f"Received signal {signum}, shutting down...")
    if scheduler:
        scheduler.shutdown()
    sys.exit(0)

def main():
    """Main entry point for the application."""
    try:
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        
        initialize_services()
        
        scheduler.schedule_daily_summary(generate_and_post_summary)
        
        scheduler.start()
        
        logging.info("Application started")
        logging.info(f"Current time in HKT: {get_hkt_time()}")
        
        while True:
            monitor_commits()
            time.sleep(3600)  # Sleep for an hour
    except Exception as e:
        logging.error(f"Application error: {str(e)}")
        if scheduler:
            scheduler.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()
