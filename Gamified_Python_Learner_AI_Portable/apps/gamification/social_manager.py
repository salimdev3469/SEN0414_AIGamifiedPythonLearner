"""
Social Manager - Handles friend requests and social features
"""

from .models import Friendship
from django.db.models import Q
from .badge_engine import check_badges


class SocialManager:
    """
    Manager for social features like friendships and friend leaderboards.
    """
    
    @staticmethod
    def send_friend_request(from_user, to_user):
        """
        Send a friend request.
        
        Args:
            from_user: User sending the request
            to_user: User receiving the request
        
        Returns:
            dict: Result with success status and message
        """
        # Check if users are the same
        if from_user == to_user:
            return {
                'success': False,
                'error': 'You cannot send a friend request to yourself'
            }
        
        # Check if friendship already exists
        existing = Friendship.objects.filter(
            Q(user=from_user, friend=to_user) |
            Q(user=to_user, friend=from_user)
        ).first()
        
        if existing:
            if existing.status == 'accepted':
                return {
                    'success': False,
                    'error': 'You are already friends'
                }
            elif existing.status == 'pending':
                return {
                    'success': False,
                    'error': 'Friend request already pending'
                }
            elif existing.status == 'rejected':
                # Allow resending after rejection
                existing.status = 'pending'
                existing.save()
                return {
                    'success': True,
                    'message': 'Friend request sent'
                }
        
        # Create new friend request
        Friendship.objects.create(
            user=from_user,
            friend=to_user,
            status='pending'
        )
        
        return {
            'success': True,
            'message': 'Friend request sent'
        }
    
    @staticmethod
    def accept_friend_request(user, requester):
        """
        Accept a friend request.
        
        Args:
            user: User accepting the request
            requester: User who sent the request
        
        Returns:
            dict: Result with success status
        """
        try:
            friendship = Friendship.objects.get(
                user=requester,
                friend=user,
                status='pending'
            )
            
            friendship.status = 'accepted'
            friendship.save()
            
            # Check for friend-related badges
            check_badges(user)
            check_badges(requester)
            
            return {
                'success': True,
                'message': 'Friend request accepted'
            }
        except Friendship.DoesNotExist:
            return {
                'success': False,
                'error': 'Friend request not found'
            }
    
    @staticmethod
    def reject_friend_request(user, requester):
        """
        Reject a friend request.
        
        Args:
            user: User rejecting the request
            requester: User who sent the request
        
        Returns:
            dict: Result with success status
        """
        try:
            friendship = Friendship.objects.get(
                user=requester,
                friend=user,
                status='pending'
            )
            
            friendship.status = 'rejected'
            friendship.save()
            
            return {
                'success': True,
                'message': 'Friend request rejected'
            }
        except Friendship.DoesNotExist:
            return {
                'success': False,
                'error': 'Friend request not found'
            }
    
    @staticmethod
    def remove_friend(user, friend):
        """
        Remove a friend.
        
        Args:
            user: User removing the friend
            friend: Friend to remove
        
        Returns:
            dict: Result with success status
        """
        # Find friendship in either direction
        friendship = Friendship.objects.filter(
            Q(user=user, friend=friend) | Q(user=friend, friend=user),
            status='accepted'
        ).first()
        
        if friendship:
            friendship.delete()
            return {
                'success': True,
                'message': 'Friend removed'
            }
        else:
            return {
                'success': False,
                'error': 'Friendship not found'
            }
    
    @staticmethod
    def get_friends(user):
        """
        Get list of user's friends.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: Friend users
        """
        from apps.authentication.models import User
        
        # Get friendships where user is either sender or receiver
        friendships = Friendship.objects.filter(
            Q(user=user) | Q(friend=user),
            status='accepted'
        )
        
        # Extract friend user IDs
        friend_ids = []
        for friendship in friendships:
            if friendship.user == user:
                friend_ids.append(friendship.friend.id)
            else:
                friend_ids.append(friendship.user.id)
        
        # Return friend users
        return User.objects.filter(id__in=friend_ids)
    
    @staticmethod
    def get_pending_requests(user):
        """
        Get pending friend requests for a user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: Pending friend requests
        """
        return Friendship.objects.filter(
            friend=user,
            status='pending'
        ).select_related('user')
    
    @staticmethod
    def get_sent_requests(user):
        """
        Get friend requests sent by a user.
        
        Args:
            user: User object
        
        Returns:
            QuerySet: Sent friend requests
        """
        return Friendship.objects.filter(
            user=user,
            status='pending'
        ).select_related('friend')
    
    @staticmethod
    def get_friend_leaderboard(user, limit=10):
        """
        Get leaderboard of user's friends.
        
        Args:
            user: User object
            limit: Number of friends to return
        
        Returns:
            list: Friends sorted by XP
        """
        friends = SocialManager.get_friends(user)
        
        # Include the user themselves
        from apps.authentication.models import User
        users = list(friends) + [user]
        
        # Sort by XP
        users.sort(key=lambda u: (-u.xp, -u.level))
        
        # Return limited results
        return users[:limit]
    
    @staticmethod
    def search_users(query, exclude_user=None, limit=20):
        """
        Search for users by username.
        
        Args:
            query: Search query
            exclude_user: User to exclude from results
            limit: Maximum results
        
        Returns:
            QuerySet: Matching users
        """
        from apps.authentication.models import User
        
        users = User.objects.filter(
            username__icontains=query
        )
        
        if exclude_user:
            users = users.exclude(id=exclude_user.id)
        
        users = users.order_by('username')[:limit]
        
        return users
    
    @staticmethod
    def get_friendship_status(user1, user2):
        """
        Get friendship status between two users.
        
        Args:
            user1: First user
            user2: Second user
        
        Returns:
            str: Status (none/pending/accepted/rejected)
        """
        friendship = Friendship.objects.filter(
            Q(user=user1, friend=user2) | Q(user=user2, friend=user1)
        ).first()
        
        if friendship:
            return friendship.status
        else:
            return 'none'


# Convenience functions
def send_friend_request(from_user, to_user):
    """Send a friend request"""
    return SocialManager.send_friend_request(from_user, to_user)


def accept_friend_request(user, requester):
    """Accept a friend request"""
    return SocialManager.accept_friend_request(user, requester)


def get_friends(user):
    """Get user's friends"""
    return SocialManager.get_friends(user)


def get_friend_leaderboard(user):
    """Get friend leaderboard"""
    return SocialManager.get_friend_leaderboard(user)

