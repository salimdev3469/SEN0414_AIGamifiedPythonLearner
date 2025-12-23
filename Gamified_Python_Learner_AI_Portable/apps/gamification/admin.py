from django.contrib import admin
from .models import Badge, UserBadge, DailyStreak, Challenge, UserChallenge, Friendship


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for badges"""
    list_display = ['icon', 'name', 'badge_type', 'xp_reward', 'is_active', 'earned_count']
    list_filter = ['badge_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    def earned_count(self, obj):
        return obj.earned_by.count()
    earned_count.short_description = 'Times Earned'


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    """Admin interface for user badges"""
    list_display = ['user', 'badge', 'progress', 'earned_at']
    list_filter = ['badge', 'earned_at']
    search_fields = ['user__username', 'badge__name']
    readonly_fields = ['earned_at']


@admin.register(DailyStreak)
class DailyStreakAdmin(admin.ModelAdmin):
    """Admin interface for daily streaks"""
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    list_filter = ['last_activity_date']
    search_fields = ['user__username']
    readonly_fields = ['last_activity_date']


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    """Admin interface for challenges"""
    list_display = ['title', 'challenge_type', 'target_metric', 'target_value', 'xp_reward', 'start_date', 'end_date', 'is_active', 'participant_count']
    list_filter = ['challenge_type', 'is_active', 'start_date']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(UserChallenge)
class UserChallengeAdmin(admin.ModelAdmin):
    """Admin interface for user challenges"""
    list_display = ['user', 'challenge', 'progress', 'target_value', 'progress_percentage', 'completed', 'completed_at']
    list_filter = ['completed', 'challenge__challenge_type']
    search_fields = ['user__username', 'challenge__title']
    readonly_fields = ['started_at', 'completed_at']
    
    def target_value(self, obj):
        return obj.challenge.target_value
    target_value.short_description = 'Target'
    
    def progress_percentage(self, obj):
        return f"{obj.get_progress_percentage()}%"
    progress_percentage.short_description = 'Progress %'


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    """Admin interface for friendships"""
    list_display = ['user', 'friend', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'friend__username']
    readonly_fields = ['created_at', 'updated_at']
