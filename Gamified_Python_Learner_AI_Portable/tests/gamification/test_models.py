"""
Tests for gamification models
"""
import pytest
from datetime import date, timedelta
from django.utils import timezone
from apps.authentication.models import User
from apps.gamification.models import (
    Badge, UserBadge, DailyStreak, Challenge, UserChallenge, Friendship
)


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def other_user(db):
    """Create another test user"""
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='TestPass123!'
    )


class TestBadgeModel:
    """Tests for Badge model"""
    
    def test_badge_creation(self, db):
        """Test creating a badge"""
        badge = Badge.objects.create(
            name='Test Badge',
            description='A test badge',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'exercises_solved', 'count': 1},
            xp_reward=50,
            is_active=True
        )
        
        assert badge.id is not None
        assert badge.name == 'Test Badge'
        assert badge.badge_type == 'achievement'
    
    def test_badge_str(self, db):
        """Test badge string representation"""
        badge = Badge.objects.create(
            name='Test Badge',
            description='A test badge',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'test'},
            xp_reward=50
        )
        
        assert str(badge) == '🎯 Test Badge'
    
    def test_badge_types(self, db):
        """Test different badge types"""
        for badge_type in ['achievement', 'milestone', 'special']:
            badge = Badge.objects.create(
                name=f'{badge_type.title()} Badge',
                description='Test',
                icon='🎯',
                badge_type=badge_type,
                criteria={'type': 'test'},
                xp_reward=50
            )
            assert badge.badge_type == badge_type
    
    def test_badge_ordering(self, db):
        """Test badge ordering"""
        badge1 = Badge.objects.create(
            name='B Badge',
            description='Test',
            icon='🎯',
            badge_type='milestone',
            criteria={'type': 'test'},
            xp_reward=50
        )
        badge2 = Badge.objects.create(
            name='A Badge',
            description='Test',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'test'},
            xp_reward=50
        )
        
        badges = list(Badge.objects.all())
        # Should be ordered by badge_type then name
        assert badges[0].badge_type == 'achievement'


class TestUserBadgeModel:
    """Tests for UserBadge model"""
    
    def test_user_badge_creation(self, user, db):
        """Test creating a user badge"""
        badge = Badge.objects.create(
            name='Test Badge',
            description='Test',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'test'},
            xp_reward=50
        )
        
        user_badge = UserBadge.objects.create(
            user=user,
            badge=badge,
            progress=100
        )
        
        assert user_badge.id is not None
        assert user_badge.user == user
        assert user_badge.badge == badge
    
    def test_user_badge_str(self, user, db):
        """Test user badge string representation"""
        badge = Badge.objects.create(
            name='Test Badge',
            description='Test',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'test'},
            xp_reward=50
        )
        
        user_badge = UserBadge.objects.create(
            user=user,
            badge=badge
        )
        
        assert str(user_badge) == f'{user.username} - Test Badge'
    
    def test_user_badge_unique_together(self, user, db):
        """Test that user can't earn same badge twice"""
        badge = Badge.objects.create(
            name='Test Badge',
            description='Test',
            icon='🎯',
            badge_type='achievement',
            criteria={'type': 'test'},
            xp_reward=50
        )
        
        UserBadge.objects.create(user=user, badge=badge)
        
        with pytest.raises(Exception):
            UserBadge.objects.create(user=user, badge=badge)


class TestDailyStreakModel:
    """Tests for DailyStreak model"""
    
    def test_streak_creation(self, user):
        """Test creating a streak"""
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10
        )
        
        assert streak.id is not None
        assert streak.current_streak == 5
        assert streak.longest_streak == 10
    
    def test_streak_str(self, user):
        """Test streak string representation"""
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10
        )
        
        assert str(streak) == f'{user.username} - 5 days'
    
    def test_streak_update_same_day(self, user):
        """Test updating streak on same day"""
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=10,
            last_activity_date=date.today()
        )
        
        result = streak.update_streak()
        
        assert result == False
        assert streak.current_streak == 5
    
    def test_streak_update_continues(self, user):
        """Test updating streak when continuing"""
        yesterday = date.today() - timedelta(days=1)
        
        streak = DailyStreak.objects.create(
            user=user,
            current_streak=5,
            longest_streak=5,
            last_activity_date=yesterday
        )
        
        result = streak.update_streak()
        
        assert result == True
        assert streak.current_streak == 6
        assert streak.longest_streak == 6
    
    def test_streak_update_broken(self, user):
        """Test updating streak when broken"""
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
        assert streak.longest_streak == 10  # Longest preserved
    
    def test_streak_one_to_one(self, user):
        """Test that user can only have one streak"""
        DailyStreak.objects.create(user=user)
        
        with pytest.raises(Exception):
            DailyStreak.objects.create(user=user)


class TestChallengeModel:
    """Tests for Challenge model"""
    
    def test_challenge_creation(self, db):
        """Test creating a challenge"""
        today = date.today()
        
        challenge = Challenge.objects.create(
            title='Test Challenge',
            description='Complete 3 exercises',
            challenge_type='daily',
            start_date=today,
            end_date=today + timedelta(days=1),
            target_metric='exercises_solved',
            target_value=3,
            xp_reward=100
        )
        
        assert challenge.id is not None
        assert challenge.title == 'Test Challenge'
    
    def test_challenge_str(self, db):
        """Test challenge string representation"""
        today = date.today()
        
        challenge = Challenge.objects.create(
            title='Test Challenge',
            description='Test',
            challenge_type='daily',
            start_date=today,
            end_date=today + timedelta(days=1),
            target_metric='exercises_solved',
            target_value=3,
            xp_reward=100
        )
        
        assert str(challenge) == 'Test Challenge (daily)'
    
    def test_challenge_is_expired_not_expired(self, db):
        """Test is_expired when challenge is active"""
        today = date.today()
        
        challenge = Challenge.objects.create(
            title='Test Challenge',
            description='Test',
            challenge_type='daily',
            start_date=today,
            end_date=today + timedelta(days=1),
            target_metric='exercises_solved',
            target_value=3,
            xp_reward=100
        )
        
        assert challenge.is_expired() == False
    
    def test_challenge_is_expired_true(self, db):
        """Test is_expired when challenge has ended"""
        yesterday = date.today() - timedelta(days=1)
        
        challenge = Challenge.objects.create(
            title='Test Challenge',
            description='Test',
            challenge_type='daily',
            start_date=yesterday - timedelta(days=1),
            end_date=yesterday,
            target_metric='exercises_solved',
            target_value=3,
            xp_reward=100
        )
        
        assert challenge.is_expired() == True


class TestUserChallengeModel:
    """Tests for UserChallenge model"""
    
    @pytest.fixture
    def challenge(self, db):
        """Create a test challenge"""
        today = date.today()
        return Challenge.objects.create(
            title='Test Challenge',
            description='Test',
            challenge_type='daily',
            start_date=today,
            end_date=today + timedelta(days=1),
            target_metric='exercises_solved',
            target_value=3,
            xp_reward=100
        )
    
    def test_user_challenge_creation(self, user, challenge):
        """Test creating a user challenge"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=1
        )
        
        assert user_challenge.id is not None
        assert user_challenge.progress == 1
        assert user_challenge.completed == False
    
    def test_user_challenge_str_incomplete(self, user, challenge):
        """Test string representation when incomplete"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=1
        )
        
        assert '1/3' in str(user_challenge)
    
    def test_user_challenge_str_complete(self, user, challenge):
        """Test string representation when complete"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=3,
            completed=True
        )
        
        assert '✓' in str(user_challenge)
    
    def test_get_progress_percentage(self, user, challenge):
        """Test progress percentage calculation"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=1
        )
        
        # 1/3 = 33%
        assert user_challenge.get_progress_percentage() == 33
    
    def test_get_progress_percentage_capped(self, user, challenge):
        """Test progress percentage is capped at 100"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=5  # More than target
        )
        
        assert user_challenge.get_progress_percentage() == 100
    
    def test_check_completion_completes(self, user, challenge):
        """Test check_completion marks as complete"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=3
        )
        
        result = user_challenge.check_completion()
        
        assert result == True
        assert user_challenge.completed == True
        assert user_challenge.completed_at is not None
    
    def test_check_completion_not_complete(self, user, challenge):
        """Test check_completion when not complete"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=1
        )
        
        result = user_challenge.check_completion()
        
        assert result == False
        assert user_challenge.completed == False
    
    def test_check_completion_already_complete(self, user, challenge):
        """Test check_completion when already complete"""
        user_challenge = UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=3,
            completed=True
        )
        
        result = user_challenge.check_completion()
        
        assert result == False  # No change


class TestFriendshipModel:
    """Tests for Friendship model"""
    
    def test_friendship_creation(self, user, other_user):
        """Test creating a friendship"""
        friendship = Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        assert friendship.id is not None
        assert friendship.status == 'pending'
    
    def test_friendship_str(self, user, other_user):
        """Test friendship string representation"""
        friendship = Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        expected = f'{user.username} → {other_user.username} (pending)'
        assert str(friendship) == expected
    
    def test_friendship_statuses(self, user, other_user):
        """Test different friendship statuses"""
        for status in ['pending', 'accepted', 'rejected']:
            Friendship.objects.filter(user=user, friend=other_user).delete()
            
            friendship = Friendship.objects.create(
                user=user,
                friend=other_user,
                status=status
            )
            
            assert friendship.status == status
    
    def test_friendship_unique_together(self, user, other_user):
        """Test that duplicate friendships are not allowed"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        with pytest.raises(Exception):
            Friendship.objects.create(
                user=user,
                friend=other_user,
                status='pending'
            )
