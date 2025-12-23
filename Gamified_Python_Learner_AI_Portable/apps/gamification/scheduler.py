"""
Scheduler for automatic challenge generation at 00:00 Istanbul time
Uses APScheduler to run tasks automatically
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

logger = logging.getLogger(__name__)

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')


def generate_challenges_job():
    """
    Job to generate daily and weekly challenges.
    Runs at 00:00 Istanbul time every day.
    """
    try:
        from django.core.management import call_command
        call_command('generate_challenges', '--type', 'both')
        logger.info('Successfully generated challenges')
    except Exception as e:
        logger.error(f'Error generating challenges: {e}')


def start_scheduler():
    """
    Start the background scheduler.
    Should be called when Django starts (e.g., in apps.py ready() method).
    """
    scheduler = BackgroundScheduler(timezone=ISTANBUL_TZ)
    
    # Schedule challenge generation at 00:00 Istanbul time every day
    scheduler.add_job(
        generate_challenges_job,
        trigger=CronTrigger(hour=0, minute=0, timezone=ISTANBUL_TZ),
        id='generate_challenges',
        name='Generate Daily and Weekly Challenges',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info('Challenge scheduler started - will run at 00:00 Istanbul time daily')
    
    return scheduler

