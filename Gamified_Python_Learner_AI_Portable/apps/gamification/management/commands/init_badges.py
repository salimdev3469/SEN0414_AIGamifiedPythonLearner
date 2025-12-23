"""
Management command to initialize default badges
"""

from django.core.management.base import BaseCommand
from apps.gamification.badge_engine import BadgeEngine


class Command(BaseCommand):
    help = 'Initialize default badges in the system'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating default badges...')
        
        created_count = BadgeEngine.create_default_badges()
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} badges')
            )
        else:
            self.stdout.write(
                self.style.WARNING('All badges already exist')
            )

