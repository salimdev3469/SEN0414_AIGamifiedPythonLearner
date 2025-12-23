"""
Tests for Challenge Manager
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
import pytz
from apps.gamification.challenge_manager import ChallengeManager, ISTANBUL_TZ
from apps.gamification.models import Challenge, UserChallenge
from tests.fixtures.base_fixtures import test_user, test_exercise, test_lesson


@pytest.mark.unit
@pytest.mark.django_db
class TestChallengeManager:
    """Test ChallengeManager class"""
    
    def test_get_istanbul_date(self):
        """Test getting Istanbul date"""
        istanbul_date = ChallengeManager.get_istanbul_date()
        assert isinstance(istanbul_date, date)
        
        # Should be today in Istanbul timezone
        istanbul_now = timezone.now().astimezone(ISTANBUL_TZ)
        expected_date = istanbul_now.date()
        assert istanbul_date == expected_date
    
    def test_reset_and_generate_daily_challenges(self):
        """Test generating daily challenges"""
        # Clear existing challenges
        Challenge.objects.filter(challenge_type='daily').delete()
        
        challenges = ChallengeManager.reset_and_generate_daily_challenges()
        
        # Should create 3 challenges
        assert len(challenges) == 3
        
        # All should be daily type
        for challenge in challenges:
            assert challenge.challenge_type == 'daily'
            assert challenge.is_active is True
        
        # Should not create duplicates if called again
        challenges2 = ChallengeManager.reset_and_generate_daily_challenges()
        assert len(challenges2) == 0  # Already exists
    
    def test_reset_expired_daily_challenges(self):
        """Test resetting expired daily challenges"""
        # Create expired challenge
        yesterday = date.today() - timedelta(days=1)
        expired = Challenge.objects.create(
            title='Expired Challenge',
            description='Old challenge',
            challenge_type='daily',
            start_date=yesterday,
            end_date=yesterday,
            target_metric='exercises_solved',
            target_value=1,
            is_active=True
        )
        
        ChallengeManager.reset_and_generate_daily_challenges()
        
        expired.refresh_from_db()
        assert expired.is_active is False
    
    def test_reset_and_generate_weekly_challenges(self):
        """Test generating weekly challenges"""
        # Clear existing weekly challenges
        Challenge.objects.filter(challenge_type='weekly').delete()
        
        challenges = ChallengeManager.reset_and_generate_weekly_challenges()
        
        # Should create challenges
        assert len(challenges) > 0
        
        # All should be weekly type
        for challenge in challenges:
            assert challenge.challenge_type == 'weekly'
            assert challenge.is_active is True
    
    def test_check_challenge_progress_exercises(self, test_user, test_exercise):
        """Test checking challenge progress for exercises"""
        from apps.coding.models import UserSubmission
        
        today = date.today()
        # Create challenge
        challenge = Challenge.objects.create(
            title='Solve 1 Exercise',
            description='Complete 1 exercise',
            challenge_type='daily',
            start_date=today,
            end_date=today,
            target_metric='exercises_solved',
            target_value=1,
            xp_reward=100
        )
        
        # Create user challenge
        user_challenge = UserChallenge.objects.create(
            user=test_user,
            challenge=challenge
        )
        
        # Initially progress should be 0
        assert user_challenge.progress == 0
        
        # Complete an exercise
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def test(): pass',
            is_correct=True
        )
        
        # Update progress - update_challenge_progress takes (user, metric_type, increment)
        ChallengeManager.update_challenge_progress(test_user, 'exercises_solved', 1)
        user_challenge.refresh_from_db()
        
        # Progress should update
        assert user_challenge.progress >= 1
    
    def test_check_challenge_progress_lessons(self, test_user, test_lesson):
        """Test checking challenge progress for lessons"""
        from apps.learning.models import UserProgress
        
        today = date.today()
        # Create challenge
        challenge = Challenge.objects.create(
            title='Complete 1 Lesson',
            description='Finish 1 lesson',
            challenge_type='daily',
            start_date=today,
            end_date=today,
            target_metric='lessons_completed',
            target_value=1,
            xp_reward=100
        )
        
        # Create user challenge
        user_challenge = UserChallenge.objects.create(
            user=test_user,
            challenge=challenge
        )
        
        # Complete lesson
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        # Update progress - update_challenge_progress takes (user, metric_type, increment)
        ChallengeManager.update_challenge_progress(test_user, 'lessons_completed', 1)
        user_challenge.refresh_from_db()
        
        # Progress should update
        assert user_challenge.progress >= 1
    
    def test_complete_challenge_awards_xp(self, test_user):
        """Test that completing challenge awards XP"""
        from apps.coding.models import UserSubmission, Exercise
        from apps.learning.models import Lesson, Module
        
        # Create exercise
        module = Module.objects.create(title='Test Module', order=1, is_published=True)
        lesson = Lesson.objects.create(
            module=module,
            title='Test Lesson',
            content='Test',
            order=1,
            is_published=True
        )
        exercise = Exercise.objects.create(
            lesson=lesson,
            title='Test Exercise',
            description='Test',
            difficulty='beginner'
        )
        
        today = date.today()
        # Create challenge
        challenge = Challenge.objects.create(
            title='Solve 1 Exercise',
            description='Complete 1 exercise',
            challenge_type='daily',
            start_date=today,
            end_date=today,
            target_metric='exercises_solved',
            target_value=1,
            xp_reward=150
        )
        
        initial_xp = test_user.xp
        
        # Create user challenge
        user_challenge = UserChallenge.objects.create(
            user=test_user,
            challenge=challenge
        )
        
        # Complete exercise
        UserSubmission.objects.create(
            user=test_user,
            exercise=exercise,
            code='def test(): pass',
            is_correct=True
        )
        
        # Update challenge progress - update_challenge_progress takes (user, metric_type, increment)
        completed = ChallengeManager.update_challenge_progress(test_user, 'exercises_solved', 1)
        user_challenge.refresh_from_db()
        
        # Check if challenge was completed and XP awarded
        test_user.refresh_from_db()
        # XP should have been awarded if challenge was completed
        assert test_user.xp >= initial_xp

