"""
Unit tests for learning models methods
"""
import pytest
from apps.learning.models import Module, Lesson, UserProgress
from apps.authentication.models import User


@pytest.mark.unit
@pytest.mark.django_db
class TestModuleMethods:
    """Test Module model methods"""
    
    def test_module_get_lessons(self, test_module, test_lesson):
        """Test get_lessons method"""
        lessons = test_module.get_lessons()
        assert test_lesson in lessons
    
    def test_module_get_lessons_only_published(self, test_module):
        """Test get_lessons only returns published lessons"""
        # Create unpublished lesson
        unpublished = Lesson.objects.create(
            module=test_module,
            title='Unpublished',
            content='Test',
            order=2,
            is_published=False,
            xp_reward=50
        )
        
        lessons = test_module.get_lessons()
        assert unpublished not in lessons
    
    def test_module_get_completion_percentage(self, test_user, test_module, test_lesson):
        """Test get_completion_percentage method"""
        # Initially 0%
        completion = test_module.get_completion_percentage(test_user)
        assert completion == 0
        
        # Complete one lesson
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        completion = test_module.get_completion_percentage(test_user)
        assert completion == 100  # 1/1 = 100%
    
    def test_module_get_completion_percentage_partial(self, test_user, test_module):
        """Test get_completion_percentage with partial completion"""
        # Create 3 lessons
        lesson1 = Lesson.objects.create(
            module=test_module,
            title='Lesson 1',
            content='Content 1',
            order=1,
            is_published=True,
            xp_reward=50
        )
        lesson2 = Lesson.objects.create(
            module=test_module,
            title='Lesson 2',
            content='Content 2',
            order=2,
            is_published=True,
            xp_reward=50
        )
        lesson3 = Lesson.objects.create(
            module=test_module,
            title='Lesson 3',
            content='Content 3',
            order=3,
            is_published=True,
            xp_reward=50
        )
        
        # Complete 2 out of 3
        UserProgress.objects.create(user=test_user, lesson=lesson1, status='completed')
        UserProgress.objects.create(user=test_user, lesson=lesson2, status='completed')
        
        completion = test_module.get_completion_percentage(test_user)
        assert 65 <= completion <= 67  # ~66.67%


@pytest.mark.unit
@pytest.mark.django_db
class TestLessonMethods:
    """Test Lesson model methods"""
    
    def test_lesson_is_completed_by(self, test_user, test_lesson):
        """Test is_completed_by method"""
        # Initially not completed
        assert test_lesson.is_completed_by(test_user) is False
        
        # Mark as completed
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        # Now should be completed
        assert test_lesson.is_completed_by(test_user) is True
    
    def test_lesson_get_next_lesson(self, test_module, test_lesson):
        """Test get_next_lesson method"""
        next_lesson = Lesson.objects.create(
            module=test_module,
            title='Next Lesson',
            content='Content',
            order=2,
            is_published=True,
            xp_reward=50
        )
        
        next = test_lesson.get_next_lesson()
        assert next == next_lesson
    
    def test_lesson_get_next_lesson_none(self, test_module, test_lesson):
        """Test get_next_lesson returns None if no next lesson"""
        # test_lesson is the only lesson
        next = test_lesson.get_next_lesson()
        assert next is None
    
    def test_lesson_get_previous_lesson(self, test_module, test_lesson):
        """Test get_previous_lesson method"""
        previous_lesson = Lesson.objects.create(
            module=test_module,
            title='Previous Lesson',
            content='Content',
            order=0,
            is_published=True,
            xp_reward=50
        )
        
        previous = test_lesson.get_previous_lesson()
        assert previous == previous_lesson
    
    def test_lesson_get_previous_lesson_none(self, test_module, test_lesson):
        """Test get_previous_lesson returns None if no previous lesson"""
        # test_lesson is first lesson
        previous = test_lesson.get_previous_lesson()
        assert previous is None


@pytest.mark.unit
@pytest.mark.django_db
class TestUserProgressMethods:
    """Test UserProgress model methods"""
    
    def test_userprogress_str_representation(self, test_user, test_lesson):
        """Test UserProgress __str__ method"""
        progress = UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        str_repr = str(progress)
        assert test_user.username in str_repr
        assert test_lesson.title in str_repr
        assert 'completed' in str_repr
    
    def test_userprogress_mark_completed(self, test_user, test_lesson):
        """Test mark_completed method"""
        progress = UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='not_started'
        )
        
        initial_xp = test_user.xp
        result = progress.mark_completed()
        
        assert result is True
        progress.refresh_from_db()
        assert progress.status == 'completed'
        assert progress.completed_at is not None
        
        test_user.refresh_from_db()
        assert test_user.xp > initial_xp
        assert test_user.total_lessons_completed == 1
    
    def test_userprogress_mark_completed_twice(self, test_user, test_lesson):
        """Test mark_completed doesn't award XP twice"""
        progress = UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        initial_xp = test_user.xp
        result = progress.mark_completed()
        
        assert result is False  # Already completed
        test_user.refresh_from_db()
        assert test_user.xp == initial_xp  # XP should not increase
    
    def test_userprogress_mark_in_progress(self, test_user, test_lesson):
        """Test mark_in_progress method"""
        progress = UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='not_started'
        )
        
        progress.mark_in_progress()
        progress.refresh_from_db()
        
        assert progress.status == 'in_progress'
        assert progress.started_at is not None
    
    def test_userprogress_mark_in_progress_from_completed(self, test_user, test_lesson):
        """Test mark_in_progress doesn't change completed status"""
        progress = UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        progress.mark_in_progress()
        progress.refresh_from_db()
        
        # Should stay completed
        assert progress.status == 'completed'

