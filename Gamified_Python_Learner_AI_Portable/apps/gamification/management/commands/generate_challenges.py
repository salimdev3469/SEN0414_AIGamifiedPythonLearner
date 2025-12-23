"""
Management command to generate daily and weekly challenges
Run this daily via cron job at 00:00 Istanbul time
"""

from django.core.management.base import BaseCommand
from apps.gamification.challenge_manager import ChallengeManager
import pytz
from datetime import timedelta
from django.utils import timezone

ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')


class Command(BaseCommand):
    help = 'Generate daily and weekly challenges (Istanbul timezone)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['daily', 'weekly', 'both'],
            default='both',
            help='Type of challenges to generate'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if challenges exist'
        )
    
    def handle(self, *args, **options):
        challenge_type = options['type']
        force = options.get('force', False)
        
        # Get current Istanbul time
        istanbul_now = timezone.now().astimezone(ISTANBUL_TZ)
        self.stdout.write(f'Current Istanbul time: {istanbul_now.strftime("%Y-%m-%d %H:%M:%S %Z")}')
        
        if challenge_type in ['daily', 'both']:
            self.stdout.write('Resetting and generating daily challenges...')
            
            if force:
                # Force reset: deactivate all existing daily challenges for today
                from apps.gamification.models import Challenge
                today = ChallengeManager.get_istanbul_date()
                Challenge.objects.filter(
                    challenge_type='daily',
                    start_date=today
                ).update(is_active=False)
            
            daily = ChallengeManager.reset_and_generate_daily_challenges()
            if daily:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {len(daily)} daily challenges')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Daily challenges already exist for today')
                )
        
        if challenge_type in ['weekly', 'both']:
            self.stdout.write('Resetting and generating weekly challenges...')
            
            if force:
                # Force reset: deactivate all existing weekly challenges for this week
                from apps.gamification.models import Challenge
                today = ChallengeManager.get_istanbul_date()
                start_of_week = today - timedelta(days=today.weekday())
                Challenge.objects.filter(
                    challenge_type='weekly',
                    start_date=start_of_week
                ).update(is_active=False)
            
            weekly = ChallengeManager.reset_and_generate_weekly_challenges()
            if weekly:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {len(weekly)} weekly challenges')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Weekly challenges already exist for this week')
                )
        
        # Deactivate expired challenges
        self.stdout.write('Deactivating expired challenges...')
        expired_count = ChallengeManager.deactivate_expired_challenges()
        if expired_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Deactivated {expired_count} expired challenges')
            )

