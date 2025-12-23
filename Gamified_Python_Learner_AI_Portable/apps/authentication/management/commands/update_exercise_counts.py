from django.core.management.base import BaseCommand
from apps.authentication.models import User
from apps.coding.models import UserSubmission


class Command(BaseCommand):
    help = 'Updates total_exercises_completed count for all users based on their correct submissions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Updating exercise completion counts..."))
        users = User.objects.all()
        updated_count = 0
        
        for user in users:
            # Count unique exercises with correct submissions
            correct_submissions = UserSubmission.objects.filter(
                user=user,
                is_correct=True
            ).values('exercise').distinct()
            
            actual_count = correct_submissions.count()
            old_count = user.total_exercises_completed
            
            if actual_count != old_count:
                user.total_exercises_completed = actual_count
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  Updated {user.username}: {old_count} -> {actual_count} exercises"
                    )
                )
                updated_count += 1
            else:
                self.stdout.write(f"  {user.username}: {actual_count} exercises - No change")
        
        self.stdout.write(self.style.SUCCESS(f"\nSuccessfully updated {updated_count} users"))




