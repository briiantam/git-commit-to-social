"""Scheduler for running tasks at specified times."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from ..config.config import get_summary_schedule_time

class Scheduler:
    """Scheduler for running tasks at specified times."""
    
    def __init__(self):
        """Initialize the Scheduler."""
        self.scheduler = BackgroundScheduler()
        logging.info("Scheduler initialized")
    
    def schedule_daily_summary(self, task):
        """
        Schedule a task to run daily at the specified time.
        
        Args:
            task (callable): The task to run.
        """
        schedule_time = get_summary_schedule_time()
        
        trigger = CronTrigger(
            hour=schedule_time["hour"],
            minute=schedule_time["minute"],
            timezone=schedule_time["timezone"]
        )
        
        self.scheduler.add_job(
            task,
            trigger=trigger,
            id="daily_summary",
            replace_existing=True
        )
        
        logging.info(f"Scheduled daily summary task for {schedule_time['hour']}:{schedule_time['minute']} HKT")
    
    def start(self):
        """Start the scheduler."""
        self.scheduler.start()
        logging.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logging.info("Scheduler shutdown")
