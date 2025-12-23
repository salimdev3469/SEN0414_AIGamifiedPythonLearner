"""
Django management command to generate comprehensive Python curriculum using Gemini API.
"""

from django.core.management.base import BaseCommand
from apps.learning.models import Module, Lesson
from apps.learning.utils import get_gemini_generator
import time


class Command(BaseCommand):
    help = 'Generate comprehensive Python curriculum using Gemini API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate all lessons (will delete existing content)',
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Generate content for a specific module by title',
        )
        parser.add_argument(
            '--lesson',
            type=int,
            help='Generate content for a specific lesson by ID',
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        generator = get_gemini_generator()
        
        if options['lesson']:
            # Generate single lesson
            self.generate_single_lesson(generator, options['lesson'])
        elif options['module']:
            # Generate all lessons in a module
            self.generate_module_lessons(generator, options['module'])
        else:
            # Generate complete curriculum
            self.generate_complete_curriculum(generator, options['regenerate'])
    
    def generate_single_lesson(self, generator, lesson_id):
        """Generate content for a single lesson."""
        try:
            lesson = Lesson.objects.get(id=lesson_id)
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Lesson with ID {lesson_id} not found'))
            return
        
        self.stdout.write(f'Generating content for: {lesson.title}...')
        
        content = generator.generate_lesson_content(
            topic=lesson.title,
            difficulty='beginner',
            estimated_time=lesson.estimated_time
        )
        
        if content:
            lesson.content = content
            lesson.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Generated content for: {lesson.title}'))
        else:
            self.stdout.write(self.style.ERROR(f'✗ Failed to generate content for: {lesson.title}'))
    
    def generate_module_lessons(self, generator, module_title):
        """Generate content for all lessons in a module."""
        try:
            module = Module.objects.get(title__icontains=module_title)
        except Module.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Module "{module_title}" not found'))
            return
        
        lessons = module.get_lessons()
        self.stdout.write(f'\nGenerating {lessons.count()} lessons for module: {module.title}\n')
        
        for lesson in lessons:
            self.stdout.write(f'Generating: {lesson.title}...')
            
            content = generator.generate_lesson_content(
                topic=lesson.title,
                difficulty='beginner',
                estimated_time=lesson.estimated_time
            )
            
            if content:
                lesson.content = content
                lesson.save()
                self.stdout.write(self.style.SUCCESS(f'  ✓ Done'))
            else:
                self.stdout.write(self.style.ERROR(f'  ✗ Failed'))
            
            # Rate limiting (Gemini API)
            time.sleep(2)
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Module "{module.title}" complete!'))
    
    def generate_complete_curriculum(self, generator, regenerate=False):
        """Generate content for the entire curriculum."""
        
        if regenerate:
            confirm = input('This will DELETE all existing lesson content. Continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write('Cancelled.')
                return
        
        # Define comprehensive curriculum
        curriculum = [
            {
                'title': 'Python Fundamentals',
                'description': 'Master the building blocks of Python programming.',
                'order': 1,
                'lessons': [
                    ('Welcome to Python', 10, 50),
                    ('Variables and Data Types', 15, 75),
                    ('Operators and Expressions', 20, 100),
                    ('String Manipulation', 20, 100),
                    ('User Input and Output', 15, 75),
                ]
            },
            {
                'title': 'Control Flow',
                'description': 'Learn to control program flow with conditions and loops.',
                'order': 2,
                'lessons': [
                    ('Conditional Statements (if/elif/else)', 25, 125),
                    ('Loops (for and while)', 30, 150),
                    ('Break, Continue, and Pass', 20, 100),
                    ('Nested Loops and Logic', 25, 125),
                ]
            },
            {
                'title': 'Functions and Modularity',
                'description': 'Write reusable code with functions.',
                'order': 3,
                'lessons': [
                    ('Defining and Calling Functions', 25, 125),
                    ('Function Parameters and Arguments', 30, 150),
                    ('Return Values and Scope', 25, 125),
                    ('Lambda Functions', 20, 100),
                    ('Decorators Basics', 25, 125),
                ]
            },
            {
                'title': 'Data Structures',
                'description': 'Master Python\'s powerful built-in data structures.',
                'order': 4,
                'lessons': [
                    ('Lists and List Operations', 30, 150),
                    ('Tuples and Named Tuples', 20, 100),
                    ('Dictionaries and Hash Tables', 30, 150),
                    ('Sets and Frozen Sets', 20, 100),
                    ('List Comprehensions', 25, 125),
                    ('Dictionary and Set Comprehensions', 20, 100),
                ]
            },
            {
                'title': 'Object-Oriented Programming',
                'description': 'Learn OOP principles and create powerful classes.',
                'order': 5,
                'lessons': [
                    ('Classes and Objects', 30, 150),
                    ('Attributes and Methods', 25, 125),
                    ('Inheritance and Polymorphism', 30, 150),
                    ('Encapsulation and Abstraction', 25, 125),
                    ('Magic Methods', 25, 125),
                    ('Property Decorators', 20, 100),
                ]
            },
            {
                'title': 'File Handling and I/O',
                'description': 'Work with files, directories, and external data.',
                'order': 6,
                'lessons': [
                    ('Reading and Writing Files', 25, 125),
                    ('Working with CSV Files', 20, 100),
                    ('JSON Data Handling', 25, 125),
                    ('File Paths and os Module', 20, 100),
                ]
            },
            {
                'title': 'Error Handling',
                'description': 'Handle errors gracefully and write robust code.',
                'order': 7,
                'lessons': [
                    ('Try-Except Blocks', 25, 125),
                    ('Exception Types', 20, 100),
                    ('Finally and Else Clauses', 20, 100),
                    ('Raising Exceptions', 20, 100),
                    ('Custom Exceptions', 25, 125),
                ]
            },
        ]
        
        self.stdout.write(self.style.WARNING('\n🚀 Starting Comprehensive Curriculum Generation\n'))
        self.stdout.write('=' * 60)
        
        total_lessons = sum(len(m['lessons']) for m in curriculum)
        current = 0
        
        for module_data in curriculum:
            # Create or get module
            module, created = Module.objects.get_or_create(
                title=module_data['title'],
                defaults={
                    'description': module_data['description'],
                    'order': module_data['order'],
                    'is_published': True,
                }
            )
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'\n📚 {action} Module: {module.title}')
            self.stdout.write('-' * 60)
            
            # Generate lessons
            for order, (title, est_time, xp) in enumerate(module_data['lessons'], start=1):
                current += 1
                progress = f'[{current}/{total_lessons}]'
                
                lesson, created = Lesson.objects.get_or_create(
                    module=module,
                    title=title,
                    defaults={
                        'estimated_time': est_time,
                        'xp_reward': xp,
                        'order': order,
                        'is_published': True,
                    }
                )
                
                if regenerate or not lesson.content or lesson.content.strip() == '':
                    self.stdout.write(f'{progress} Generating: {title}...')
                    
                    content = generator.generate_lesson_content(
                        topic=title,
                        difficulty='beginner',
                        estimated_time=est_time
                    )
                    
                    if content:
                        lesson.content = content
                        lesson.estimated_time = est_time
                        lesson.xp_reward = xp
                        lesson.order = order
                        lesson.save()
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Success! ({len(content)} chars)'))
                    else:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed'))
                    
                    # Rate limiting
                    time.sleep(2)
                else:
                    self.stdout.write(f'{progress} Skipped: {title} (already has content)')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('\n✅ Curriculum Generation Complete!\n'))
        self.stdout.write(f'Total Modules: {Module.objects.count()}')
        self.stdout.write(f'Total Lessons: {Lesson.objects.count()}')
        self.stdout.write(f'Total Lessons with Content: {Lesson.objects.exclude(content="").count()}\n')

