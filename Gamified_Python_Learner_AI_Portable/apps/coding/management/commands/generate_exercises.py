from django.core.management.base import BaseCommand
from apps.learning.models import Lesson, Module
from apps.coding.models import Exercise, TestCase
from apps.learning.utils import get_exercise_generator
import time
import json


class Command(BaseCommand):
    help = 'Generate coding exercises for lessons using Gemini API'

    def add_arguments(self, parser):
        parser.add_argument('--lesson', type=int, help='Generate exercises for a specific lesson ID')
        parser.add_argument('--module', type=str, help='Generate exercises for all lessons in a module')
        parser.add_argument('--regenerate', action='store_true', help='Regenerate all exercises (deletes existing)')
        parser.add_argument('--num', type=int, default=None, help='Number of exercises per lesson (auto if not specified)')
        parser.add_argument('--min-exercises', type=int, default=5, help='Minimum exercises per lesson (default: 5)')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Starting Exercise Generation with Gemini AI"))
        self.stdout.write(self.style.SUCCESS("="*60))

        generator = get_exercise_generator()

        # Handle regeneration
        if options['regenerate']:
            self.stdout.write(self.style.WARNING("🧹 Clearing existing exercises..."))
            TestCase.objects.all().delete()
            Exercise.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("✅ Exercises cleared!\n"))

        # Get lessons to process
        if options['lesson']:
            lessons = Lesson.objects.filter(id=options['lesson'], is_published=True)
        elif options['module']:
            module = Module.objects.filter(title=options['module']).first()
            if not module:
                self.stdout.write(self.style.ERROR(f"Module '{options['module']}' not found!"))
                return
            lessons = Lesson.objects.filter(module=module, is_published=True).order_by('order')
        else:
            lessons = Lesson.objects.filter(is_published=True).order_by('module__order', 'order')

        total_lessons = lessons.count()
        if total_lessons == 0:
            self.stdout.write(self.style.WARNING("No lessons found!"))
            return

        self.stdout.write(self.style.SUCCESS(f"📚 Processing {total_lessons} lessons\n"))

        total_exercises_created = 0
        total_test_cases_created = 0

        for idx, lesson in enumerate(lessons, 1):
            self.stdout.write(self.style.HTTP_INFO(f"\n[{idx}/{total_lessons}] {lesson.module.title} → {lesson.title}"))
            self.stdout.write("-" * 60)

            # Check if exercises already exist
            existing_count = Exercise.objects.filter(lesson=lesson).count()
            min_exercises = options.get('min_exercises', 5)
            
            if existing_count >= min_exercises and not options['regenerate']:
                self.stdout.write(self.style.SUCCESS(f"  ✅ {existing_count} exercises (>= {min_exercises} required). Skipping..."))
                continue
            elif existing_count > 0 and not options['regenerate']:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Only {existing_count} exercises found (need {min_exercises}). Generating more..."))

            try:
                # Generate exercises using Gemini
                self.stdout.write(f"  🤖 Asking Gemini to generate exercises...")
                exercises_data = generator.generate_exercises_for_lesson(
                    lesson_title=lesson.title,
                    lesson_content=lesson.content,
                    num_exercises=options['num']
                )

                if not exercises_data:
                    self.stdout.write(self.style.ERROR(f"  ❌ Failed to generate exercises"))
                    continue

                # Create exercises
                for ex_idx, ex_data in enumerate(exercises_data, 1):
                    try:
                        # Create exercise
                        exercise = Exercise.objects.create(
                            lesson=lesson,
                            title=ex_data.get('title', f'Exercise {ex_idx}'),
                            description=ex_data.get('description', ''),
                            difficulty=ex_data.get('difficulty', 'easy'),
                            xp_reward=ex_data.get('xp_reward', 50),
                            starter_code=ex_data.get('starter_code', '# Write your code here\ndef solution():\n    pass'),
                            solution_code=ex_data.get('solution_code', ''),
                            hints=ex_data.get('hints', []),
                            expected_approach=ex_data.get('expected_approach', ''),
                            order=ex_idx,
                            is_published=True
                        )
                        total_exercises_created += 1

                        # Create test cases with validation
                        test_cases = ex_data.get('test_cases', [])
                        for tc_idx, tc_data in enumerate(test_cases, 1):
                            # Validate and provide default values for empty fields
                            input_data = tc_data.get('input', '') or tc_data.get('input_data', '')
                            expected_output = tc_data.get('expected_output', '')
                            
                            # Skip test case if both input and output are empty/None
                            if not input_data and not expected_output:
                                self.stdout.write(self.style.WARNING(
                                    f"    ⚠️  Skipping empty test case {tc_idx}"
                                ))
                                continue
                            
                            # Provide meaningful defaults
                            if not input_data:
                                input_data = 'No input required'
                            if not expected_output:
                                expected_output = 'See description'
                            
                            TestCase.objects.create(
                                exercise=exercise,
                                input_data=input_data,
                                expected_output=expected_output,
                                is_hidden=tc_data.get('is_hidden', False),
                                order=tc_idx
                            )
                            total_test_cases_created += 1

                        self.stdout.write(self.style.SUCCESS(
                            f"  ✅ {exercise.get_difficulty_display_emoji} {exercise.title} "
                            f"({len(test_cases)} tests, {exercise.xp_reward} XP)"
                        ))

                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ❌ Error creating exercise: {e}"))
                        continue

                # Rate limiting
                time.sleep(3)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Error: {e}"))
                continue

        # Summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("✅ EXERCISE GENERATION COMPLETE!"))
        self.stdout.write(self.style.SUCCESS("="*60))
        self.stdout.write(self.style.SUCCESS(f"📊 Statistics:"))
        self.stdout.write(self.style.SUCCESS(f"  Total Lessons Processed: {total_lessons}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Exercises Created: {total_exercises_created}"))
        self.stdout.write(self.style.SUCCESS(f"  Total Test Cases Created: {total_test_cases_created}"))
        self.stdout.write(self.style.SUCCESS(f"  Average Exercises per Lesson: {total_exercises_created / total_lessons if total_lessons > 0 else 0:.1f}"))
        self.stdout.write(self.style.SUCCESS("\n🎉 Done! Your exercises are ready for students!"))

