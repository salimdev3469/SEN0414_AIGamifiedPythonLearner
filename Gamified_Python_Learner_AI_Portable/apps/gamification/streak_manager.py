"""
Streak Manager - Handles daily streak tracking and updates
"""

from datetime import date, timedelta
from .models import DailyStreak
from .badge_engine import check_badges


class StreakManager:
    """
    Manager for handling user activity streaks.
    """
    
    @staticmethod
    def update_streak(user):
        """
        Update user's streak based on current activity.
        
        Args:
            user: User object
        
        Returns:
            dict: Streak information
        """
        # Get or create streak record
        streak, created = DailyStreak.objects.get_or_create(
            user=user,
            defaults={
                'current_streak': 1,
                'longest_streak': 1,
                'last_activity_date': date.today()
            }
        )
        
        if created:
            # New streak record
            return {
                'current_streak': 1,
                'longest_streak': 1,
                'streak_continued': True,
                'streak_broken': False
            }
        
        # Update existing streak
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        if streak.last_activity_date == today:
            # Already counted today
            return {
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
                'streak_continued': False,
                'streak_broken': False
            }
        
        streak_continued = False
        streak_broken = False
        
        if streak.last_activity_date == yesterday:
            # Continue streak
            streak.current_streak += 1
            streak_continued = True
        elif streak.last_activity_date < yesterday:
            # Streak broken, reset
            streak.current_streak = 1
            streak_broken = True
        
        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        
        streak.last_activity_date = today
        streak.save()
        
        # Check for streak-related badges
        check_badges(user)
        
        return {
            'current_streak': streak.current_streak,
            'longest_streak': streak.longest_streak,
            'streak_continued': streak_continued,
            'streak_broken': streak_broken
        }
    
    @staticmethod
    def get_streak_info(user):
        """
        Get streak information for a user.
        
        Args:
            user: User object
        
        Returns:
            dict: Streak information
        """
        try:
            streak = DailyStreak.objects.get(user=user)
            
            # Check if streak is still active
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            is_active = streak.last_activity_date in [today, yesterday]
            
            return {
                'current_streak': streak.current_streak,
                'longest_streak': streak.longest_streak,
                'last_activity_date': streak.last_activity_date,
                'is_active': is_active
            }
        except DailyStreak.DoesNotExist:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'last_activity_date': None,
                'is_active': False
            }
    
    @staticmethod
    def check_broken_streaks():
        """
        Check all users for broken streaks (to be run daily via cron).
        
        Returns:
            int: Number of streaks reset
        """
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # Find streaks that should be broken
        broken_streaks = DailyStreak.objects.filter(
            last_activity_date__lt=yesterday,
            current_streak__gt=0
        )
        
        count = broken_streaks.count()
        
        # Reset broken streaks
        broken_streaks.update(current_streak=0)
        
        return count


# Convenience functions
def update_user_streak(user):
    """Update streak for a user"""
    return StreakManager.update_streak(user)


def get_user_streak(user):
    """Get streak info for a user"""
    return StreakManager.get_streak_info(user)

