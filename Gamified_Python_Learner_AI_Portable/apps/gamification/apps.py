from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gamification'
    
    def ready(self):
        """
        Start the scheduler when Django app is ready.
        Runs automatically in production, or when ENABLE_SCHEDULER env var is set.
        """
        import os
        from django.conf import settings
        
        # Start scheduler if:
        # 1. Not in test mode (settings.TESTING)
        # 2. ENABLE_SCHEDULER env var is set to 'True'
        # 3. Or in production (not DEBUG)
        enable_scheduler = (
            os.getenv('ENABLE_SCHEDULER', 'False') == 'True' or
            not settings.DEBUG
        )
        
        # Don't start in test mode
        if hasattr(settings, 'TESTING') and settings.TESTING:
            enable_scheduler = False
        
        if enable_scheduler:
            try:
                from .scheduler import start_scheduler
                start_scheduler()
                logger.info('Challenge scheduler started - will run at 00:00 Istanbul time daily')
            except Exception as e:
                logger.warning(f'Could not start challenge scheduler: {e}')
                # Scheduler is optional, don't fail if it can't start
