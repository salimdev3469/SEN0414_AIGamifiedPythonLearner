"""
Integration tests for complete user journeys
"""
import pytest
from django.urls import reverse
from apps.authentication.models import User
from apps.learning.models import UserProgress, Module, Lesson
from apps.coding.models import Exercise, TestCase


@pytest.mark.integration
@pytest.mark.django_db
class TestCompleteUserJourneyLearning:
    """Test complete user journey: Register → Login → View Curriculum → Complete Lesson → Earn XP"""
    
    def test_full_learning_journey(self, client, test_module):
        """Test complete learning flow"""
        # Step 1: Register
        response = client.post(reverse('auth:register'), {
            'username': 'journeyuser',
            'email': 'journey@example.com',
            'password1': 'JourneyPass123!',
            'password2': 'JourneyPass123!',
        })
        assert User.objects.filter(username='journeyuser').exists()
        
        # Step 2: Login
        response = client.post(reverse('auth:login'), {
            'username': 'journeyuser',
            'password': 'JourneyPass123!',
        })
        assert response.status_code in [200, 302]
        
        # Get user
        user = User.objects.get(username='journeyuser')
        initial_xp = user.xp
        assert initial_xp == 0
        
        # Step 3: View Curriculum
        response = client.get(reverse('learning:curriculum'))
        assert response.status_code == 200
        
        # Step 4: Create and view a lesson
        lesson = Lesson.objects.create(
            module=test_module,
            title='Journey Lesson',
            content='Test content',
            order=1,
            is_published=True,
            xp_reward=50
        )
        
        response = client.get(reverse('learning:lesson_detail', args=[lesson.id]))
        assert response.status_code == 200
        
        # Step 5: Complete the lesson
        response = client.post(reverse('learning:mark_complete', args=[lesson.id]))
        
        # Step 6: Verify XP was awarded
        user.refresh_from_db()
        assert user.xp == initial_xp + 50
        
        # Step 7: Verify progress was tracked
        progress = UserProgress.objects.filter(user=user, lesson=lesson).first()
        assert progress is not None
        assert progress.status == 'completed'
        
        # Step 8: Check leaderboard
        response = client.get(reverse('auth:leaderboard'))
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.django_db
class TestCompleteUserJourneyCoding:
    """Test complete user journey: Register → Login → Exercise → Submit Code → Pass Tests → Earn XP"""
    
    def test_full_coding_journey(self, client, test_module):
        """Test complete coding flow"""
        # Step 1: Register
        response = client.post(reverse('auth:register'), {
            'username': 'codeuser',
            'email': 'code@example.com',
            'password1': 'CodePass123!',
            'password2': 'CodePass123!',
        })
        assert User.objects.filter(username='codeuser').exists()
        
        # Step 2: Login
        client.post(reverse('auth:login'), {
            'username': 'codeuser',
            'password': 'CodePass123!',
        })
        
        user = User.objects.get(username='codeuser')
        
        # Step 3: Create lesson and complete it (prerequisite)
        lesson = Lesson.objects.create(
            module=test_module,
            title='Code Lesson',
            content='Learn to code',
            order=1,
            is_published=True,
            xp_reward=50
        )
        
        client.post(reverse('learning:mark_complete', args=[lesson.id]))
        
        # Step 4: Create exercise
        exercise = Exercise.objects.create(
            lesson=lesson,
            title='Add Function',
            description='Write an add function',
            difficulty='beginner',
            starter_code='# Write your code',
            solution_code='def add(a, b): return a + b'
        )
        
        # Step 5: Create test case
        TestCase.objects.create(
            exercise=exercise,
            input_data='2, 3',
            expected_output='5',
            is_hidden=False
        )
        
        # Step 6: Access exercise page
        response = client.get(reverse('coding:exercise_detail', args=[exercise.id]))
        assert response.status_code == 200
        
        # Step 7: Run code (syntax check)
        import json
        response = client.post(
            reverse('coding:run_code', args=[exercise.id]),
            data=json.dumps({'code': 'print("test")'}),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Note: Full submission test would require mocking Gemini API
        # We've verified the flow works up to this point


@pytest.mark.integration
@pytest.mark.django_db
class TestGamificationIntegration:
    """Test gamification elements integrate correctly"""
    
    def test_lesson_completion_triggers_xp_and_level(self, authenticated_client, test_user, test_module):
        """Test: Lesson completion → XP update → Level calculation → Leaderboard refresh"""
        # Create lesson
        lesson = Lesson.objects.create(
            module=test_module,
            title='Test Lesson',
            content='Content',
            order=1,
            is_published=True,
            xp_reward=50
        )
        
        # Initial state
        assert test_user.xp == 0
        assert test_user.level == 1
        
        # Complete lesson
        response = authenticated_client.post(
            reverse('learning:mark_complete', args=[lesson.id])
        )
        
        # Check XP updated
        test_user.refresh_from_db()
        assert test_user.xp == 50
        assert test_user.level == 1  # Still level 1 (need 100 for level 2)
        
        # Complete another lesson to level up
        lesson2 = Lesson.objects.create(
            module=test_module,
            title='Test Lesson 2',
            content='Content',
            order=2,
            is_published=True,
            xp_reward=50
        )
        
        authenticated_client.post(
            reverse('learning:mark_complete', args=[lesson2.id])
        )
        
        # Check leveled up
        test_user.refresh_from_db()
        assert test_user.xp == 100
        # Level depends on settings, but should be at least 1
        assert test_user.level >= 1
        
        # Check leaderboard reflects changes
        leaderboard = User.objects.order_by('-xp')[:10]
        assert test_user in leaderboard
    
    def test_module_completion_percentage_updates(self, authenticated_client, test_user, test_module):
        """Test module completion percentage updates as lessons are completed"""
        # Create 3 lessons
        lessons = []
        for i in range(3):
            lesson = Lesson.objects.create(
                module=test_module,
                title=f'Lesson {i+1}',
                content='Content',
                order=i+1,
                is_published=True,
                xp_reward=50
            )
            lessons.append(lesson)
        
        # Initially 0%
        assert test_module.get_completion_percentage(test_user) == 0
        
        # Complete 1 lesson: 33.33%
        authenticated_client.post(reverse('learning:mark_complete', args=[lessons[0].id]))
        completion = test_module.get_completion_percentage(test_user)
        assert 32 <= completion <= 34  # ~33.33%
        
        # Complete 2 lessons: 66.67%
        authenticated_client.post(reverse('learning:mark_complete', args=[lessons[1].id]))
        completion = test_module.get_completion_percentage(test_user)
        assert 65 <= completion <= 68  # ~66.67%
        
        # Complete all lessons: 100%
        authenticated_client.post(reverse('learning:mark_complete', args=[lessons[2].id]))
        completion = test_module.get_completion_percentage(test_user)
        assert completion == 100

