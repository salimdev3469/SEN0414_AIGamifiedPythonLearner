"""
Management command to award badges retroactively to existing users
"""

from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.gamification.badge_engine import check_badges


class Command(BaseCommand):
    help = 'Award badges retroactively to all existing users based on their current progress'
    
    def handle(self, *args, **options):
        self.stdout.write('Checking badges for all users...')
        
        users = User.objects.all()
        total_badges_awarded = 0
        
        for user in users:
            self.stdout.write(f'\nChecking user: {user.username}')
            
            # Check and award all eligible badges
            newly_earned = check_badges(user)
            
            if newly_earned:
                for badge in newly_earned:
                    self.stdout.write(
                        self.style.SUCCESS(f'  Awarded: {badge.name} (+{badge.xp_reward} XP)')
                    )
                    total_badges_awarded += 1
            else:
                self.stdout.write('  No new badges')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal badges awarded: {total_badges_awarded}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Users processed: {users.count()}')
        )

