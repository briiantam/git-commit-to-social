"""Configuration module for the git-commit-to-social project."""
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

REPO_PATH = os.getenv("REPO_PATH", "/home/ubuntu/repos/barebone-ai-app")

DAILY_SUMMARY_TIME_HKT = os.getenv("DAILY_SUMMARY_TIME_HKT", "22:30")
HKT_TIMEZONE = pytz.timezone("Asia/Hong_Kong")

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "commits.db")

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs", "app.log")

def get_hkt_time():
    """Get the current time in HKT timezone."""
    return datetime.now(HKT_TIMEZONE)

def get_summary_schedule_time():
    """Get the scheduled time for daily summary in HKT."""
    hour, minute = map(int, DAILY_SUMMARY_TIME_HKT.split(":"))
    return {
        "hour": hour,
        "minute": minute,
        "timezone": HKT_TIMEZONE
    }
