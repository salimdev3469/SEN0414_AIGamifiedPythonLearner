"""
Management command to check and reset broken streaks
Run this daily via cron job
"""

from django.core.management.base import BaseCommand
from apps.gamification.streak_manager import StreakManager


class Command(BaseCommand):
    help = 'Check and reset broken streaks (run daily)'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking for broken streaks...')
        
        count = StreakManager.check_broken_streaks()
        
        if count > 0:
            self.stdout.write(
                self.style.WARNING(f'Reset {count} broken streaks')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('No broken streaks found')
            )

