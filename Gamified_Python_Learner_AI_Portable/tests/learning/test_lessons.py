"""
Unit tests for learning module (lessons and progress)
"""
import pytest
from django.urls import reverse
from apps.learning.models import UserProgress


@pytest.mark.unit
@pytest.mark.django_db
class TestLessonCompletion:
    """Test lesson completion functionality"""
    
    def test_lesson_completion_creates_progress(self, authenticated_client, test_lesson, test_user):
        """Test that completing a lesson creates UserProgress record"""
        response = authenticated_client.post(
            reverse('learning:mark_complete', args=[test_lesson.id])
        )
        
        # Check UserProgress was created
        progress = UserProgress.objects.filter(
            user=test_user,
            lesson=test_lesson
        ).first()
        
        assert progress is not None
        assert progress.status == 'completed'
    
    def test_lesson_completion_awards_xp(self, authenticated_client, test_lesson, test_user):
        """Test that completing a lesson awards XP"""
        initial_xp = test_user.xp
        
        response = authenticated_client.post(
            reverse('learning:mark_complete', args=[test_lesson.id])
        )
        
        # Refresh user profile
        test_user.refresh_from_db()
        
        # Check XP increased (should be +50)
        assert test_user.xp == initial_xp + 50
    
    def test_lesson_completion_twice_no_double_xp(self, authenticated_client, test_lesson, test_user):
        """Test that completing same lesson twice doesn't award XP twice"""
        # Complete first time
        authenticated_client.post(
            reverse('learning:mark_complete', args=[test_lesson.id])
        )
        
        test_user.refresh_from_db()
        xp_after_first = test_user.xp
        
        # Complete second time
        authenticated_client.post(
            reverse('learning:mark_complete', args=[test_lesson.id])
        )
        
        test_user.refresh_from_db()
        xp_after_second = test_user.xp
        
        # XP should be the same
        assert xp_after_first == xp_after_second
    
    def test_lesson_is_completed_by(self, test_user, test_lesson):
        """Test lesson.is_completed_by() method"""
        # Initially not completed
        assert not test_lesson.is_completed_by(test_user)
        
        # Create completion record
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        # Now should be completed
        assert test_lesson.is_completed_by(test_user)


@pytest.mark.unit
@pytest.mark.django_db
class TestProgressTracking:
    """Test progress tracking functionality"""
    
    def test_module_completion_percentage(self, test_user, test_module):
        """Test module completion percentage calculation"""
        # Create 3 lessons
        from apps.learning.models import Lesson
        lesson1 = Lesson.objects.create(module=test_module, title='Lesson 1', order=1, is_published=True, xp_reward=50)
        lesson2 = Lesson.objects.create(module=test_module, title='Lesson 2', order=2, is_published=True, xp_reward=50)
        lesson3 = Lesson.objects.create(module=test_module, title='Lesson 3', order=3, is_published=True, xp_reward=50)
        
        # Complete 1 out of 3 lessons
        UserProgress.objects.create(user=test_user, lesson=lesson1, status='completed')
        
        # Check completion percentage
        completion = test_module.get_completion_percentage(test_user)
        assert completion == pytest.approx(33.33, rel=0.1)  # 1/3 = 33.33%
    
    def test_module_completion_zero_when_no_progress(self, test_user, test_module, test_lesson):
        """Test module completion is 0% with no progress"""
        completion = test_module.get_completion_percentage(test_user)
        assert completion == 0
    
    def test_module_completion_100_when_all_done(self, test_user, test_module):
        """Test module completion is 100% when all lessons done"""
        from apps.learning.models import Lesson
        lesson1 = Lesson.objects.create(module=test_module, title='Lesson 1', order=1, is_published=True, xp_reward=50)
        lesson2 = Lesson.objects.create(module=test_module, title='Lesson 2', order=2, is_published=True, xp_reward=50)
        
        # Complete all lessons
        UserProgress.objects.create(user=test_user, lesson=lesson1, status='completed')
        UserProgress.objects.create(user=test_user, lesson=lesson2, status='completed')
        
        completion = test_module.get_completion_percentage(test_user)
        assert completion == 100
    
    def test_user_total_completed_lessons(self, test_user, test_module):
        """Test counting total completed lessons"""
        from apps.learning.models import Lesson
        lesson1 = Lesson.objects.create(module=test_module, title='Lesson 1', order=1, is_published=True, xp_reward=50)
        lesson2 = Lesson.objects.create(module=test_module, title='Lesson 2', order=2, is_published=True, xp_reward=50)
        lesson3 = Lesson.objects.create(module=test_module, title='Lesson 3', order=3, is_published=True, xp_reward=50)
        
        # Complete 2 lessons
        UserProgress.objects.create(user=test_user, lesson=lesson1, status='completed')
        UserProgress.objects.create(user=test_user, lesson=lesson2, status='completed')
        
        total_completed = UserProgress.objects.filter(
            user=test_user,
            status='completed'
        ).count()
        
        assert total_completed == 2

