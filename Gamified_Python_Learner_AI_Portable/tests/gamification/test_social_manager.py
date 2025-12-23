"""
Tests for social manager
"""
import pytest
from apps.authentication.models import User
from apps.gamification.models import Friendship
from apps.gamification.social_manager import (
    SocialManager,
    send_friend_request,
    accept_friend_request,
    get_friends,
    get_friend_leaderboard
)


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!',
        xp=100
    )


@pytest.fixture
def other_user(db):
    """Create another test user"""
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='TestPass123!',
        xp=200
    )


@pytest.fixture
def third_user(db):
    """Create a third test user"""
    return User.objects.create_user(
        username='thirduser',
        email='third@example.com',
        password='TestPass123!',
        xp=300
    )


class TestSendFriendRequest:
    """Tests for SocialManager.send_friend_request"""
    
    def test_send_request_success(self, user, other_user):
        """Test successful friend request"""
        result = SocialManager.send_friend_request(user, other_user)
        
        assert result['success'] == True
        assert result['message'] == 'Friend request sent'
        assert Friendship.objects.filter(
            user=user,
            friend=other_user,
            status='pending'
        ).exists()
    
    def test_send_request_to_self(self, user):
        """Test cannot send request to self"""
        result = SocialManager.send_friend_request(user, user)
        
        assert result['success'] == False
        assert 'yourself' in result['error']
    
    def test_send_request_already_friends(self, user, other_user):
        """Test cannot send request if already friends"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        result = SocialManager.send_friend_request(user, other_user)
        
        assert result['success'] == False
        assert 'already friends' in result['error']
    
    def test_send_request_already_pending(self, user, other_user):
        """Test cannot send request if already pending"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        result = SocialManager.send_friend_request(user, other_user)
        
        assert result['success'] == False
        assert 'already pending' in result['error']
    
    def test_send_request_after_rejection(self, user, other_user):
        """Test can resend request after rejection"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='rejected'
        )
        
        result = SocialManager.send_friend_request(user, other_user)
        
        assert result['success'] == True
        friendship = Friendship.objects.get(user=user, friend=other_user)
        assert friendship.status == 'pending'
    
    def test_send_request_reverse_direction_pending(self, user, other_user):
        """Test cannot send request if other user already sent one"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        result = SocialManager.send_friend_request(user, other_user)
        
        assert result['success'] == False


class TestAcceptFriendRequest:
    """Tests for SocialManager.accept_friend_request"""
    
    def test_accept_request_success(self, user, other_user):
        """Test successful acceptance"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        result = SocialManager.accept_friend_request(user, other_user)
        
        assert result['success'] == True
        friendship = Friendship.objects.get(user=other_user, friend=user)
        assert friendship.status == 'accepted'
    
    def test_accept_nonexistent_request(self, user, other_user):
        """Test accepting nonexistent request"""
        result = SocialManager.accept_friend_request(user, other_user)
        
        assert result['success'] == False
        assert 'not found' in result['error']
    
    def test_accept_already_accepted(self, user, other_user):
        """Test cannot accept already accepted request"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='accepted'
        )
        
        result = SocialManager.accept_friend_request(user, other_user)
        
        assert result['success'] == False


class TestRejectFriendRequest:
    """Tests for SocialManager.reject_friend_request"""
    
    def test_reject_request_success(self, user, other_user):
        """Test successful rejection"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        result = SocialManager.reject_friend_request(user, other_user)
        
        assert result['success'] == True
        friendship = Friendship.objects.get(user=other_user, friend=user)
        assert friendship.status == 'rejected'
    
    def test_reject_nonexistent_request(self, user, other_user):
        """Test rejecting nonexistent request"""
        result = SocialManager.reject_friend_request(user, other_user)
        
        assert result['success'] == False
        assert 'not found' in result['error']


class TestRemoveFriend:
    """Tests for SocialManager.remove_friend"""
    
    def test_remove_friend_success(self, user, other_user):
        """Test successful friend removal"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        result = SocialManager.remove_friend(user, other_user)
        
        assert result['success'] == True
        assert not Friendship.objects.filter(
            user=user,
            friend=other_user
        ).exists()
    
    def test_remove_friend_reverse_direction(self, user, other_user):
        """Test removing friend when friendship is in reverse direction"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='accepted'
        )
        
        result = SocialManager.remove_friend(user, other_user)
        
        assert result['success'] == True
    
    def test_remove_nonexistent_friend(self, user, other_user):
        """Test removing nonexistent friend"""
        result = SocialManager.remove_friend(user, other_user)
        
        assert result['success'] == False
        assert 'not found' in result['error']
    
    def test_remove_friend_not_accepted(self, user, other_user):
        """Test cannot remove friend with pending status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        result = SocialManager.remove_friend(user, other_user)
        
        assert result['success'] == False


class TestGetFriends:
    """Tests for SocialManager.get_friends"""
    
    def test_get_friends_as_sender(self, user, other_user):
        """Test getting friends when user is sender"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        friends = SocialManager.get_friends(user)
        
        assert len(friends) == 1
        assert other_user in friends
    
    def test_get_friends_as_receiver(self, user, other_user):
        """Test getting friends when user is receiver"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='accepted'
        )
        
        friends = SocialManager.get_friends(user)
        
        assert len(friends) == 1
        assert other_user in friends
    
    def test_get_friends_multiple(self, user, other_user, third_user):
        """Test getting multiple friends"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        Friendship.objects.create(
            user=third_user,
            friend=user,
            status='accepted'
        )
        
        friends = SocialManager.get_friends(user)
        
        assert len(friends) == 2
    
    def test_get_friends_excludes_pending(self, user, other_user):
        """Test that pending friendships are excluded"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        friends = SocialManager.get_friends(user)
        
        assert len(friends) == 0
    
    def test_get_friends_empty(self, user):
        """Test getting friends when none exist"""
        friends = SocialManager.get_friends(user)
        
        assert len(friends) == 0


class TestGetPendingRequests:
    """Tests for SocialManager.get_pending_requests"""
    
    def test_get_pending_requests(self, user, other_user):
        """Test getting pending requests"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        pending = SocialManager.get_pending_requests(user)
        
        assert len(pending) == 1
        assert pending[0].user == other_user
    
    def test_get_pending_requests_empty(self, user):
        """Test getting pending requests when none exist"""
        pending = SocialManager.get_pending_requests(user)
        
        assert len(pending) == 0


class TestGetSentRequests:
    """Tests for SocialManager.get_sent_requests"""
    
    def test_get_sent_requests(self, user, other_user):
        """Test getting sent requests"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        sent = SocialManager.get_sent_requests(user)
        
        assert len(sent) == 1
        assert sent[0].friend == other_user
    
    def test_get_sent_requests_empty(self, user):
        """Test getting sent requests when none exist"""
        sent = SocialManager.get_sent_requests(user)
        
        assert len(sent) == 0


class TestGetFriendLeaderboard:
    """Tests for SocialManager.get_friend_leaderboard"""
    
    def test_get_friend_leaderboard(self, user, other_user, third_user):
        """Test getting friend leaderboard"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        Friendship.objects.create(
            user=user,
            friend=third_user,
            status='accepted'
        )
        
        leaderboard = SocialManager.get_friend_leaderboard(user)
        
        # Should include user and friends, sorted by XP
        assert len(leaderboard) == 3
        assert leaderboard[0] == third_user  # 300 XP
        assert leaderboard[1] == other_user  # 200 XP
        assert leaderboard[2] == user  # 100 XP
    
    def test_get_friend_leaderboard_includes_self(self, user):
        """Test that leaderboard includes the user"""
        leaderboard = SocialManager.get_friend_leaderboard(user)
        
        assert len(leaderboard) == 1
        assert user in leaderboard
    
    def test_get_friend_leaderboard_limit(self, user, other_user, third_user):
        """Test leaderboard limit"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        Friendship.objects.create(
            user=user,
            friend=third_user,
            status='accepted'
        )
        
        leaderboard = SocialManager.get_friend_leaderboard(user, limit=2)
        
        assert len(leaderboard) == 2


class TestSearchUsers:
    """Tests for SocialManager.search_users"""
    
    def test_search_users_by_username(self, user, other_user):
        """Test searching users by username"""
        results = SocialManager.search_users('other')
        
        assert len(results) == 1
        assert other_user in results
    
    def test_search_users_case_insensitive(self, user, other_user):
        """Test that search is case insensitive"""
        results = SocialManager.search_users('OTHER')
        
        assert len(results) == 1
        assert other_user in results
    
    def test_search_users_exclude_user(self, user, other_user):
        """Test excluding a user from results"""
        results = SocialManager.search_users('user', exclude_user=user)
        
        assert user not in results
        assert other_user in results
    
    def test_search_users_limit(self, db):
        """Test search limit"""
        for i in range(25):
            User.objects.create_user(
                username=f'searchuser{i}',
                email=f'search{i}@example.com',
                password='TestPass123!'
            )
        
        results = SocialManager.search_users('searchuser', limit=10)
        
        assert len(results) == 10
    
    def test_search_users_no_results(self, user):
        """Test search with no results"""
        results = SocialManager.search_users('nonexistent')
        
        assert len(results) == 0


class TestGetFriendshipStatus:
    """Tests for SocialManager.get_friendship_status"""
    
    def test_status_none(self, user, other_user):
        """Test status when no friendship exists"""
        status = SocialManager.get_friendship_status(user, other_user)
        
        assert status == 'none'
    
    def test_status_pending(self, user, other_user):
        """Test pending status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='pending'
        )
        
        status = SocialManager.get_friendship_status(user, other_user)
        
        assert status == 'pending'
    
    def test_status_accepted(self, user, other_user):
        """Test accepted status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        status = SocialManager.get_friendship_status(user, other_user)
        
        assert status == 'accepted'
    
    def test_status_rejected(self, user, other_user):
        """Test rejected status"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='rejected'
        )
        
        status = SocialManager.get_friendship_status(user, other_user)
        
        assert status == 'rejected'
    
    def test_status_reverse_direction(self, user, other_user):
        """Test status check in reverse direction"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='accepted'
        )
        
        status = SocialManager.get_friendship_status(user, other_user)
        
        assert status == 'accepted'


class TestConvenienceFunctions:
    """Tests for convenience functions"""
    
    def test_send_friend_request_function(self, user, other_user):
        """Test send_friend_request convenience function"""
        result = send_friend_request(user, other_user)
        
        assert result['success'] == True
    
    def test_accept_friend_request_function(self, user, other_user):
        """Test accept_friend_request convenience function"""
        Friendship.objects.create(
            user=other_user,
            friend=user,
            status='pending'
        )
        
        result = accept_friend_request(user, other_user)
        
        assert result['success'] == True
    
    def test_get_friends_function(self, user, other_user):
        """Test get_friends convenience function"""
        Friendship.objects.create(
            user=user,
            friend=other_user,
            status='accepted'
        )
        
        friends = get_friends(user)
        
        assert len(friends) == 1
    
    def test_get_friend_leaderboard_function(self, user):
        """Test get_friend_leaderboard convenience function"""
        leaderboard = get_friend_leaderboard(user)
        
        assert len(leaderboard) == 1
