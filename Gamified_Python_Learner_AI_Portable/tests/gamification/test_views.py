"""
Tests for gamification views
"""
import pytest
from django.urls import reverse
from django.test import Client
from apps.authentication.models import User
from apps.gamification.models import Badge, UserBadge, Challenge, UserChallenge, Friendship, DailyStreak
from apps.learning.models import Module, Lesson, UserProgress
from apps.coding.models import Exercise, UserSubmission
from datetime import date, timedelta


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


@pytest.fixture
def third_user(db):
    """Create a third test user"""
    return User.objects.create_user(
        username='thirduser',
        email='third@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def badge(db):
    """Create a test badge"""
    return Badge.objects.create(
        name='Test Badge',
        description='A test badge',
        icon='🎯',
        badge_type='achievement',
        criteria={'type': 'exercises_solved', 'count': 1},
        xp_reward=50,
        is_active=True
    )


@pytest.fixture
def challenge(db):
    """Create a test challenge"""
    today = date.today()
    return Challenge.objects.create(
        title='Test Challenge',
        description='Complete 3 exercises',
        challenge_type='daily',
        start_date=today,
        end_date=today + timedelta(days=1),
        target_metric='exercises_solved',
        target_value=3,
        xp_reward=100,
        is_active=True
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a client with authenticated user"""
    client.force_login(user)
    return client


@pytest.fixture
def module(db):
    """Create a test module"""
    return Module.objects.create(
        title='Test Module',
        description='Test module description',
        order=1,
        is_published=True
    )


@pytest.fixture
def lesson(db, module):
    """Create a test lesson"""
    return Lesson.objects.create(
        module=module,
        title='Test Lesson',
        content='Test content',
        order=1,
        is_published=True
    )


@pytest.fixture
def exercise(db, lesson):
    """Create a test exercise"""
    return Exercise.objects.create(
        lesson=lesson,
        title='Test Exercise',
        description='Test description',
        difficulty='easy',
        order=1
    )


class TestBadgesView:
    """Tests for badges_view"""
    
    def test_badges_view_requires_login(self, client):
        """Test that badges view requires login"""
        response = client.get(reverse('gamification:badges'))
        assert response.status_code == 302
        assert '/auth/login/' in response.url
    
    def test_badges_view_shows_all_badges(self, authenticated_client, badge):
        """Test that badges view shows all active badges"""
        response = authenticated_client.get(reverse('gamification:badges'))
        assert response.status_code == 200
        assert 'badges_with_progress' in response.context
        assert len(response.context['badges_with_progress']) == 1
    
    def test_badges_view_shows_earned_count(self, authenticated_client, user, badge):
        """Test that badges view shows correct earned count"""
        # Award the badge to the user
        UserBadge.objects.create(user=user, badge=badge)
        
        response = authenticated_client.get(reverse('gamification:badges'))
        assert response.status_code == 200
        assert response.context['earned_count'] == 1
        assert response.context['total_count'] == 1
    
    def test_badges_view_progress_for_unearned(self, authenticated_client, badge):
        """Test progress display for unearned badges"""
        response = authenticated_client.get(reverse('gamification:badges'))
        assert response.status_code == 200
        
        badge_data = response.context['badges_with_progress'][0]
        assert badge_data['progress']['earned'] == False


class TestChallengesView:
    """Tests for challenges_view"""
    
    def test_challenges_view_requires_login(self, client):
        """Test that challenges view requires login"""
        response = client.get(reverse('gamification:challenges'))
        assert response.status_code == 302
    
    def test_challenges_view_shows_daily_challenges(self, authenticated_client, challenge):
        """Test that challenges view shows daily challenges"""
        response = authenticated_client.get(reverse('gamification:challenges'))
        assert response.status_code == 200
        assert 'daily_challenges' in response.context
    
    def test_challenges_view_shows_weekly_challenges(self, authenticated_client, db):
        """Test that challenges view shows weekly challenges"""
        today = date.today()
        Challenge.objects.create(
            title='Weekly Challenge',
            description='Weekly test',
            challenge_type='weekly',
            start_date=today,
            end_date=today + timedelta(days=7),
            target_metric='lessons_completed',
            target_value=5,
            xp_reward=200,
            is_active=True
        )
        
        response = authenticated_client.get(reverse('gamification:challenges'))
        assert response.status_code == 200
        assert 'weekly_challenges' in response.context
    
    def test_challenges_view_shows_completed(self, authenticated_client, user, challenge):
        """Test that completed challenges are shown"""
        UserChallenge.objects.create(
            user=user,
            challenge=challenge,
            progress=3,
            completed=True
        )
        
        response = authenticated_client.get(reverse('gamification:challenges'))
        assert response.status_code == 200
        assert 'completed_challenges' in response.context


class TestFriendsView:
    """Tests for friends_view"""
    
    def test_friends_view_requires_login(self, client):
        """Test that friends view requires login"""
        response = client.get(reverse('gamification:friends'))
        assert response.status_code == 302
    
    def test_friends_view_shows_friends_list(self, authenticated_client, user, other_user):
        """Test that friends view shows friends"""
        # Create accepted friendship
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        response = authenticated_client.get(reverse('gamification:friends'))
        assert response.status_code == 200
        assert 'friends' in response.context
    
    def test_friends_view_shows_pending_requests(self, authenticated_client, user, other_user):
        """Test that friends view shows pending requests"""
        # Create pending request from other_user to user
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        response = authenticated_client.get(reverse('gamification:friends'))
        assert response.status_code == 200
        assert 'pending_requests' in response.context
        assert len(response.context['pending_requests']) == 1
    
    def test_friends_view_shows_sent_requests(self, authenticated_client, user, other_user):
        """Test that friends view shows sent requests"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        response = authenticated_client.get(reverse('gamification:friends'))
        assert response.status_code == 200
        assert 'sent_requests' in response.context
        assert len(response.context['sent_requests']) == 1


class TestFriendSearchView:
    """Tests for friend_search_view"""
    
    def test_friend_search_requires_login(self, client):
        """Test that friend search requires login"""
        response = client.get(reverse('gamification:friend_search'))
        assert response.status_code == 302
    
    def test_friend_search_short_query(self, authenticated_client):
        """Test that short queries are rejected"""
        response = authenticated_client.get(
            reverse('gamification:friend_search') + '?q=a'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == False
        assert 'at least 2 characters' in data['error']
    
    def test_friend_search_empty_query(self, authenticated_client):
        """Test that empty queries are rejected"""
        response = authenticated_client.get(
            reverse('gamification:friend_search') + '?q='
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == False
    
    def test_friend_search_finds_users(self, authenticated_client, other_user):
        """Test that search finds matching users"""
        response = authenticated_client.get(
            reverse('gamification:friend_search') + '?q=other'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert len(data['users']) == 1
        assert data['users'][0]['username'] == 'otheruser'
    
    def test_friend_search_includes_friendship_status(self, authenticated_client, user, other_user):
        """Test that search includes friendship status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        response = authenticated_client.get(
            reverse('gamification:friend_search') + '?q=other'
        )
        data = response.json()
        assert data['users'][0]['friendship_status'] == 'accepted'


class TestSendFriendRequestView:
    """Tests for send_friend_request_view"""
    
    def test_send_request_requires_login(self, client, other_user):
        """Test that sending request requires login"""
        response = client.post(
            reverse('gamification:send_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
    
    def test_send_request_success(self, authenticated_client, user, other_user):
        """Test successful friend request"""
        response = authenticated_client.post(
            reverse('gamification:send_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302  # Redirect
        
        # Check friendship was created
        assert Friendship.objects.filter(
            user=user,
            friend=other_user,
            status='pending'
        ).exists()
    
    def test_send_request_ajax(self, authenticated_client, other_user):
        """Test AJAX friend request"""
        response = authenticated_client.post(
            reverse('gamification:send_friend_request', kwargs={'user_id': other_user.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
    
    def test_send_request_to_nonexistent_user(self, authenticated_client):
        """Test sending request to nonexistent user"""
        response = authenticated_client.post(
            reverse('gamification:send_friend_request', kwargs={'user_id': 99999})
        )
        assert response.status_code == 404


class TestAcceptFriendRequestView:
    """Tests for accept_friend_request_view"""
    
    def test_accept_request_requires_login(self, client, other_user):
        """Test that accepting request requires login"""
        response = client.post(
            reverse('gamification:accept_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
    
    def test_accept_request_success(self, authenticated_client, user, other_user):
        """Test successful acceptance"""
        # Create pending request
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        response = authenticated_client.post(
            reverse('gamification:accept_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
        
        # Check friendship was accepted
        friendship = Friendship.objects.get(user=other_user, friend=user)
        assert friendship.status == 'accepted'
    
    def test_accept_nonexistent_request(self, authenticated_client, other_user):
        """Test accepting nonexistent request"""
        response = authenticated_client.post(
            reverse('gamification:accept_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302  # Redirects with error message


class TestRejectFriendRequestView:
    """Tests for reject_friend_request_view"""
    
    def test_reject_request_requires_login(self, client, other_user):
        """Test that rejecting request requires login"""
        response = client.post(
            reverse('gamification:reject_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
    
    def test_reject_request_success(self, authenticated_client, user, other_user):
        """Test successful rejection"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        response = authenticated_client.post(
            reverse('gamification:reject_friend_request', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
        
        friendship = Friendship.objects.get(user=other_user, friend=user)
        assert friendship.status == 'rejected'


class TestRemoveFriendView:
    """Tests for remove_friend_view"""
    
    def test_remove_friend_requires_login(self, client, other_user):
        """Test that removing friend requires login"""
        response = client.post(
            reverse('gamification:remove_friend', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
    
    def test_remove_friend_success(self, authenticated_client, user, other_user):
        """Test successful removal"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        response = authenticated_client.post(
            reverse('gamification:remove_friend', kwargs={'user_id': other_user.id})
        )
        assert response.status_code == 302
        
        assert not Friendship.objects.filter(
            user=user,
            friend=other_user,
            status='accepted'
        ).exists()
    
    def test_remove_friend_ajax(self, authenticated_client, user, other_user):
        """Test AJAX friend removal"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        response = authenticated_client.post(
            reverse('gamification:remove_friend', kwargs={'user_id': other_user.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True


class TestUserProfileView:
    """Tests for user_profile_view"""
    
    def test_profile_view_requires_login(self, client, other_user):
        """Test that profile view requires login"""
        response = client.get(
            reverse('gamification:user_profile', kwargs={'username': other_user.username})
        )
        assert response.status_code == 302
    
    def test_profile_view_shows_user_info(self, authenticated_client, other_user):
        """Test that profile view shows user info"""
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': other_user.username})
        )
        assert response.status_code == 200
        assert response.context['profile_user'] == other_user
    
    def test_profile_view_shows_badges(self, authenticated_client, other_user, badge):
        """Test that profile view shows user badges"""
        UserBadge.objects.create(user=other_user, badge=badge)
        
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': other_user.username})
        )
        assert response.status_code == 200
        assert 'user_badges' in response.context
        assert len(response.context['user_badges']) == 1
    
    def test_profile_view_shows_friendship_status(self, authenticated_client, user, other_user):
        """Test that profile view shows friendship status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': other_user.username})
        )
        assert response.status_code == 200
        assert response.context['friendship_status'] == 'accepted'
    
    def test_profile_view_own_profile(self, authenticated_client, user):
        """Test viewing own profile"""
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': user.username})
        )
        assert response.status_code == 200
        assert response.context['is_own_profile'] == True
    
    def test_profile_view_nonexistent_user(self, authenticated_client):
        """Test viewing nonexistent user profile"""
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': 'nonexistent'})
        )
        assert response.status_code == 404
    
    def test_profile_view_shows_stats(self, authenticated_client, other_user, exercise, lesson):
        """Test that profile view shows user stats"""
        # Create some submissions
        UserSubmission.objects.create(
            user=other_user,
            exercise=exercise,
            code='print("test")',
            is_correct=True
        )
        
        # Create lesson progress
        UserProgress.objects.create(
            user=other_user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.get(
            reverse('gamification:user_profile', kwargs={'username': other_user.username})
        )
        assert response.status_code == 200
        assert response.context['total_submissions'] == 1
        assert response.context['correct_submissions'] == 1
        assert response.context['lessons_completed'] == 1
