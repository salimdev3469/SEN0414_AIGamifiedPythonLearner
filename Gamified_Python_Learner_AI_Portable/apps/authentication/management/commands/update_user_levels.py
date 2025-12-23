"""
Management command to update all user levels based on their XP.
This ensures that all users have correct levels according to the current XP system.
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import User


class Command(BaseCommand):
    help = 'Update all user levels based on their current XP'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        users = User.objects.all()
        updated_count = 0
        
        self.stdout.write(f'Checking {users.count()} users...')
        
        for user in users:
            old_level = user.level
            
            # Reset level to 1 and recalculate
            user.level = 1
            user.check_level_up()
            
            if user.level != old_level:
                updated_count += 1
                if dry_run:
                    self.stdout.write(
                        f'  Would update {user.username}: Level {old_level} -> {user.level} '
                        f'(XP: {user.xp})'
                    )
                else:
                    user.save(update_fields=['level'])
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Updated {user.username}: Level {old_level} -> {user.level} '
                            f'(XP: {user.xp})'
                        )
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nWould update {updated_count} users')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully updated {updated_count} users')
            )

