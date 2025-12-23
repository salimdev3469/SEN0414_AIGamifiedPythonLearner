"""
Tests for streak manager
"""
import pytest
from datetime import date, timedelta
from apps.authentication.models import User
from apps.gamification.models import DailyStreak
from apps.gamification.streak_manager import (
    StreakManager,
    update_user_streak,
    get_user_streak
)


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


class TestStreakManagerUpdateStreak:
    """Tests for StreakManager.update_streak"""
    
    def test_update_streak_creates_new_record(self, user):
        """Test that update creates new streak record"""
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 1
        assert result['longest_streak'] == 1
        assert result['streak_continued'] == True
        assert result['streak_broken'] == False
        assert DailyStreak.objects.filter(user=user).exists()
    
    def test_update_streak_same_day(self, user):
        """Test that same-day update doesn't change streak"""
        # First update
        StreakManager.update_streak(user)
        
        # Second update same day
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 1
        assert result['streak_continued'] == False
        assert result['streak_broken'] == False
    
    def test_update_streak_continues(self, user):
        """Test streak continues when activity is consecutive"""
        yesterday = date.today() - timedelta(days=1)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_activity_date=yesterday
        )
        
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 6
        assert result['streak_continued'] == True
        assert result['streak_broken'] == False
    
    def test_update_streak_broken(self, user):
        """Test streak breaks when gap in activity"""
        two_days_ago = date.today() - timedelta(days=2)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_activity_date=two_days_ago
        )
        
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 1
        assert result['streak_broken'] == True
        assert result['streak_continued'] == False
    
    def test_update_streak_updates_longest(self, user):
        """Test that longest streak is updated"""
        yesterday = date.today() - timedelta(days=1)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_activity_date=yesterday
        )
        
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 6
        assert result['longest_streak'] == 6
    
    def test_update_streak_keeps_longest(self, user):
        """Test that longest streak is kept when current is lower"""
        two_days_ago = date.today() - timedelta(days=2)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        
        result = StreakManager.update_streak(user)
        
        assert result['current_streak'] == 1
        assert result['longest_streak'] == 10


class TestStreakManagerGetStreakInfo:
    """Tests for StreakManager.get_streak_info"""
    
    def test_get_streak_info_no_streak(self, user):
        """Test getting info when no streak exists"""
        info = StreakManager.get_streak_info(user)
        
        assert info['current_streak'] == 0
        assert info['longest_streak'] == 0
        assert info['last_activity_date'] is None
        assert info['is_active'] == False
    
    def test_get_streak_info_today(self, user):
        """Test getting info when last activity was today"""
        today = date.today()
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=today
        )
        
        info = StreakManager.get_streak_info(user)
        
        assert info['current_streak'] == 5
        assert info['longest_streak'] == 10
        assert info['last_activity_date'] == today
        assert info['is_active'] == True
    
    def test_get_streak_info_yesterday(self, user):
        """Test getting info when last activity was yesterday"""
        yesterday = date.today() - timedelta(days=1)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=yesterday
        )
        
        info = StreakManager.get_streak_info(user)
        
        assert info['current_streak'] == 5
        assert info['is_active'] == True
    
    def test_get_streak_info_inactive(self, user):
        """Test getting info when streak is inactive"""
        two_days_ago = date.today() - timedelta(days=2)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        
        info = StreakManager.get_streak_info(user)
        
        assert info['is_active'] == False


class TestStreakManagerCheckBrokenStreaks:
    """Tests for StreakManager.check_broken_streaks"""
    
    def test_check_broken_streaks(self, user, db):
        """Test checking and resetting broken streaks"""
        two_days_ago = date.today() - timedelta(days=2)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        
        count = StreakManager.check_broken_streaks()
        
        assert count == 1
        
        streak = DailyStreak.objects.get(user=user)
        assert streak.current_streak == 0
    
    def test_check_broken_streaks_keeps_active(self, user, db):
        """Test that active streaks are not reset"""
        yesterday = date.today() - timedelta(days=1)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=yesterday
        )
        
        count = StreakManager.check_broken_streaks()
        
        assert count == 0
        
        streak = DailyStreak.objects.get(user=user)
        assert streak.current_streak == 5
    
    def test_check_broken_streaks_multiple_users(self, db):
        """Test checking broken streaks for multiple users"""
        two_days_ago = date.today() - timedelta(days=2)
        yesterday = date.today() - timedelta(days=1)
        
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='TestPass123!'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPass123!'
        )
        
        DailyStreak.objects.create(
            user=user1,
            current_streak=5,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        DailyStreak.objects.create(
            user=user2,
            current_streak=3,
            longest_streak=5,
            last_activity_date=yesterday
        )
        
        count = StreakManager.check_broken_streaks()
        
        assert count == 1
        
        streak1 = DailyStreak.objects.get(user=user1)
        streak2 = DailyStreak.objects.get(user=user2)
        
        assert streak1.current_streak == 0
        assert streak2.current_streak == 3
    
    def test_check_broken_streaks_already_zero(self, user, db):
        """Test that already-zero streaks are not counted"""
        two_days_ago = date.today() - timedelta(days=2)
        
        DailyStreak.objects.create(
            user=user,
            current_streak=0,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        
        count = StreakManager.check_broken_streaks()
        
        assert count == 0


class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_update_user_streak_function(self, user):
        """Test update_user_streak convenience function"""
        result = update_user_streak(user)
        
        assert result['current_streak'] == 1
    
    def test_get_user_streak_function(self, user):
        """Test get_user_streak convenience function"""
        DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=date.today()
        )
        
        info = get_user_streak(user)
        
        assert info['current_streak'] == 5
        assert info['longest_streak'] == 10


class TestDailyStreakModel:
    """Tests for DailyStreak model methods"""
    
    def test_update_streak_method_same_day(self, user):
        """Test DailyStreak.update_streak method on same day"""
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=date.today()
        )
        
        result = streak.update_streak()
        
        assert result == False  # Already counted today
        assert streak.current_streak == 5
    
    def test_update_streak_method_continues(self, user):
        """Test DailyStreak.update_streak method continues streak"""
        yesterday = date.today() - timedelta(days=1)
        
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=yesterday
        )
        
        result = streak.update_streak()
        
        assert result == True
        assert streak.current_streak == 6
    
    def test_update_streak_method_resets(self, user):
        """Test DailyStreak.update_streak method resets broken streak"""
        two_days_ago = date.today() - timedelta(days=2)
        
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=two_days_ago
        )
        
        result = streak.update_streak()
        
        assert result == True
        assert streak.current_streak == 1
    
    def test_streak_str_representation(self, user):
        """Test DailyStreak __str__ method"""
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10
        )
        
        assert str(streak) == f"{user.username} - 5 days"
