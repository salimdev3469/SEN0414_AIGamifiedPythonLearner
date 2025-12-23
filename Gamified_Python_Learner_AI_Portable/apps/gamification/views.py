from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.authentication.models import User
from .models import Badge, UserBadge, Challenge, UserChallenge, Friendship
from .badge_engine import BadgeEngine
from .challenge_manager import get_user_challenges
from .social_manager import SocialManager


@login_required
def badges_view(request):
    """Display all badges and user's progress"""
    all_badges = Badge.objects.filter(is_active=True).order_by('badge_type', 'name')
    
    # Get user's earned badges
    earned_badge_ids = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)
    
    # Add progress info to each badge
    badges_with_progress = []
    for badge in all_badges:
        progress = BadgeEngine.get_badge_progress(request.user, badge)
        badges_with_progress.append({
            'badge': badge,
            'progress': progress
        })
    
    context = {
        'badges_with_progress': badges_with_progress,
        'earned_count': len(earned_badge_ids),
        'total_count': all_badges.count()
    }
    
    return render(request, 'gamification/badges.html', context)


@login_required
def challenges_view(request):
    """Display active challenges and user's progress"""
    challenges_with_progress = get_user_challenges(request.user)
    
    # Separate by type
    daily_challenges = [c for c in challenges_with_progress if c['challenge'].challenge_type == 'daily']
    weekly_challenges = [c for c in challenges_with_progress if c['challenge'].challenge_type == 'weekly']
    
    # Get completed challenges
    completed_challenges = UserChallenge.objects.filter(
        user=request.user,
        completed=True
    ).select_related('challenge').order_by('-completed_at')[:10]
    
    context = {
        'daily_challenges': daily_challenges,
        'weekly_challenges': weekly_challenges,
        'completed_challenges': completed_challenges
    }
    
    return render(request, 'gamification/challenges.html', context)


@login_required
def friends_view(request):
    """Display friends list and friend requests"""
    friends = SocialManager.get_friends(request.user)
    pending_requests = SocialManager.get_pending_requests(request.user)
    sent_requests = SocialManager.get_sent_requests(request.user)
    friend_leaderboard = SocialManager.get_friend_leaderboard(request.user, limit=20)
    
    context = {
        'friends': friends,
        'pending_requests': pending_requests,
        'sent_requests': sent_requests,
        'friend_leaderboard': friend_leaderboard
    }
    
    return render(request, 'gamification/friends.html', context)


@login_required
@require_http_methods(["GET"])
def friend_search_view(request):
    """Search for users to add as friends"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Search query must be at least 2 characters'
        })
    
    users = SocialManager.search_users(query, exclude_user=request.user, limit=10)
    
    # Add friendship status for each user
    results = []
    for user in users:
        status = SocialManager.get_friendship_status(request.user, user)
        results.append({
            'id': user.id,
            'username': user.username,
            'level': user.level,
            'xp': user.xp,
            'friendship_status': status
        })
    
    return JsonResponse({
        'success': True,
        'users': results
    })


@login_required
@require_http_methods(["POST"])
def send_friend_request_view(request, user_id):
    """Send a friend request"""
    to_user = get_object_or_404(User, id=user_id)
    
    result = SocialManager.send_friend_request(request.user, to_user)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse(result)
    
    # Regular form submission
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['error'])
    
    return redirect('gamification:friends')


@login_required
@require_http_methods(["POST"])
def accept_friend_request_view(request, user_id):
    """Accept a friend request"""
    requester = get_object_or_404(User, id=user_id)
    
    result = SocialManager.accept_friend_request(request.user, requester)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['error'])
    
    return redirect('gamification:friends')


@login_required
@require_http_methods(["POST"])
def reject_friend_request_view(request, user_id):
    """Reject a friend request"""
    requester = get_object_or_404(User, id=user_id)
    
    result = SocialManager.reject_friend_request(request.user, requester)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['error'])
    
    return redirect('gamification:friends')


@login_required
@require_http_methods(["POST"])
def remove_friend_view(request, user_id):
    """Remove a friend"""
    friend = get_object_or_404(User, id=user_id)
    
    result = SocialManager.remove_friend(request.user, friend)
    
    # Check if it's an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(result)
    
    # Regular form submission
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['error'])
    
    return redirect('gamification:friends')


@login_required
def user_profile_view(request, username):
    """View another user's profile"""
    profile_user = get_object_or_404(User, username=username)
    
    # Get user's badges
    user_badges = UserBadge.objects.filter(user=profile_user).select_related('badge').order_by('-earned_at')
    
    # Get friendship status
    friendship_status = SocialManager.get_friendship_status(request.user, profile_user)
    
    # Get streak info
    from .streak_manager import get_user_streak
    streak_info = get_user_streak(profile_user)
    
    # Get stats
    from apps.coding.models import UserSubmission
    from apps.learning.models import UserProgress
    
    total_submissions = UserSubmission.objects.filter(user=profile_user).count()
    correct_submissions = UserSubmission.objects.filter(user=profile_user, is_correct=True).count()
    lessons_completed = UserProgress.objects.filter(user=profile_user, status='completed').count()
    
    context = {
        'profile_user': profile_user,
        'user_badges': user_badges,
        'friendship_status': friendship_status,
        'streak_info': streak_info,
        'total_submissions': total_submissions,
        'correct_submissions': correct_submissions,
        'lessons_completed': lessons_completed,
        'is_own_profile': request.user == profile_user
    }
    
    return render(request, 'gamification/user_profile.html', context)
