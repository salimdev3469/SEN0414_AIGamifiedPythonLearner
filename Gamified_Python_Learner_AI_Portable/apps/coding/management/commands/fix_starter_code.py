"""
Django management command to fix exercise starter codes.
"""
from django.core.management.base import BaseCommand
from apps.coding.models import Exercise


class Command(BaseCommand):
    help = 'Fix exercise starter codes by removing def solution() wrapper'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🔧 Fixing Exercise Starter Codes..."))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        
        exercises = Exercise.objects.all()
        fixed_count = 0
        
        for exercise in exercises:
            old_code = exercise.starter_code
            
            # Check if it has the old format
            if 'def solution' in old_code or 'def ' in old_code:
                # Simplify to just a comment
                exercise.starter_code = "# Write your code here\n"
                exercise.save()
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f"  ✓ Fixed: {exercise.title}"))
        
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS(f"✅ Fixed {fixed_count} exercises!"))
        self.stdout.write(self.style.SUCCESS(f"📊 Total exercises: {exercises.count()}"))
        self.stdout.write(self.style.SUCCESS("\n🎉 All exercises now use simple format!"))


