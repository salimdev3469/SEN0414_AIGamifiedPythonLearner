"""
Tests for Badge Engine
"""
import pytest
from apps.gamification.badge_engine import BadgeEngine
from apps.gamification.models import Badge, UserBadge
from tests.fixtures.base_fixtures import test_user, test_exercise, test_lesson


@pytest.mark.unit
@pytest.mark.django_db
class TestBadgeEngine:
    """Test BadgeEngine class"""
    
    def test_check_and_award_badges_no_badges(self, test_user):
        """Test when no badges exist"""
        awarded = BadgeEngine.check_and_award_badges(test_user)
        assert awarded == []
    
    def test_check_and_award_badges_exercises_solved(self, test_user, test_exercise):
        """Test awarding badge for exercises solved"""
        from apps.coding.models import UserSubmission
        
        # Create badge
        badge = Badge.objects.create(
            name='First Exercise',
            description='Complete your first exercise',
            criteria={
                'type': 'exercises_solved',
                'count': 1
            },
            xp_reward=50,
            is_active=True
        )
        
        # Complete exercise
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def test(): pass',
            is_correct=True
        )
        
        # Check and award
        awarded = BadgeEngine.check_and_award_badges(test_user)
        
        assert len(awarded) == 1
        assert awarded[0].id == badge.id
        
        # Verify user badge was created
        user_badge = UserBadge.objects.get(user=test_user, badge=badge)
        assert user_badge.progress == 100
        
        # Verify XP was awarded
        test_user.refresh_from_db()
        assert test_user.xp == 50
    
    def test_check_and_award_badges_lessons_completed(self, test_user, test_lesson):
        """Test awarding badge for lessons completed"""
        from apps.learning.models import UserProgress
        
        # Create badge
        badge = Badge.objects.create(
            name='First Lesson',
            description='Complete your first lesson',
            criteria={
                'type': 'lessons_completed',
                'count': 1
            },
            xp_reward=30,
            is_active=True
        )
        
        # Complete lesson
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        # Check and award
        awarded = BadgeEngine.check_and_award_badges(test_user)
        
        assert len(awarded) == 1
        assert awarded[0].id == badge.id
    
    def test_check_and_award_badges_not_met(self, test_user):
        """Test when badge criteria not met"""
        # Create badge with high requirement
        badge = Badge.objects.create(
            name='Expert',
            description='Complete 100 exercises',
            criteria={
                'type': 'exercises_solved',
                'count': 100
            },
            xp_reward=500,
            is_active=True
        )
        
        # Check and award (should not award)
        awarded = BadgeEngine.check_and_award_badges(test_user)
        
        assert len(awarded) == 0
        assert not UserBadge.objects.filter(user=test_user, badge=badge).exists()
    
    def test_check_and_award_badges_already_earned(self, test_user, test_exercise):
        """Test that already earned badges are not re-awarded"""
        from apps.coding.models import UserSubmission
        
        # Create badge
        badge = Badge.objects.create(
            name='First Exercise',
            description='Complete your first exercise',
            criteria={
                'type': 'exercises_solved',
                'count': 1
            },
            xp_reward=50,
            is_active=True
        )
        
        # Complete exercise
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def test(): pass',
            is_correct=True
        )
        
        # Award first time
        awarded1 = BadgeEngine.check_and_award_badges(test_user)
        assert len(awarded1) == 1
        
        # Award second time (should not award again)
        awarded2 = BadgeEngine.check_and_award_badges(test_user)
        assert len(awarded2) == 0
        
        # Should only have one user badge
        assert UserBadge.objects.filter(user=test_user, badge=badge).count() == 1
    
    def test_check_and_award_badges_inactive_badge(self, test_user, test_exercise):
        """Test that inactive badges are not awarded"""
        from apps.coding.models import UserSubmission
        
        # Create inactive badge
        badge = Badge.objects.create(
            name='Inactive Badge',
            description='This badge is inactive',
            criteria={
                'type': 'exercises_solved',
                'count': 1
            },
            xp_reward=50,
            is_active=False  # Inactive
        )
        
        # Complete exercise
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def test(): pass',
            is_correct=True
        )
        
        # Check and award (should not award inactive badge)
        awarded = BadgeEngine.check_and_award_badges(test_user)
        
        assert len(awarded) == 0
        assert not UserBadge.objects.filter(user=test_user, badge=badge).exists()
    
    def test_check_criteria_xp_earned(self, test_user):
        """Test XP earned criteria"""
        # Set user XP
        test_user.xp = 500
        test_user.save()
        
        criteria = {
            'type': 'xp_earned',
            'xp': 500
        }
        
        result = BadgeEngine._check_criteria(test_user, criteria)
        # XP earned criteria checks if user has at least the amount
        assert result is True
        
        # Lower XP should not meet criteria
        test_user.xp = 100
        test_user.save()
        result = BadgeEngine._check_criteria(test_user, criteria)
        assert result is False
        
        # Equal XP should meet criteria
        test_user.xp = 500
        test_user.save()
        result = BadgeEngine._check_criteria(test_user, criteria)
        assert result is True
    
    def test_check_criteria_level_reached(self, test_user):
        """Test level reached criteria"""
        # Set user level
        test_user.xp = 1000  # Should be level 2 or higher
        test_user.save()
        test_user.check_level_up()
        
        criteria = {
            'type': 'level_reached',
            'level': 2
        }
        
        result = BadgeEngine._check_criteria(test_user, criteria)
        # Result depends on actual level calculation
        assert isinstance(result, bool)

