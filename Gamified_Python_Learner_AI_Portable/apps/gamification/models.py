from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta


class Badge(models.Model):
    """
    Represents an achievement badge that users can earn.
    """
    BADGE_TYPES = [
        ('achievement', 'Achievement'),
        ('milestone', 'Milestone'),
        ('special', 'Special'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Badge Name'
    )
    
    description = models.TextField(
        verbose_name='Description',
        help_text='What this badge represents'
    )
    
    icon = models.CharField(
        max_length=50,
        verbose_name='Icon',
        help_text='Emoji or icon class'
    )
    
    badge_type = models.CharField(
        max_length=20,
        choices=BADGE_TYPES,
        default='achievement',
        verbose_name='Badge Type'
    )
    
    criteria = models.JSONField(
        verbose_name='Criteria',
        help_text='JSON object defining how to earn this badge'
    )
    
    xp_reward = models.IntegerField(
        default=0,
        verbose_name='XP Reward',
        help_text='XP awarded when earning this badge'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'badges'
        verbose_name = 'Badge'
        verbose_name_plural = 'Badges'
        ordering = ['badge_type', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """
    Tracks badges earned by users.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
        verbose_name='User'
    )
    
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='earned_by',
        verbose_name='Badge'
    )
    
    earned_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Earned At'
    )
    
    progress = models.IntegerField(
        default=100,
        verbose_name='Progress',
        help_text='Progress percentage (0-100)'
    )
    
    class Meta:
        db_table = 'user_badges'
        verbose_name = 'User Badge'
        verbose_name_plural = 'User Badges'
        unique_together = ['user', 'badge']
        ordering = ['-earned_at']
        indexes = [
            models.Index(fields=['user', '-earned_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class DailyStreak(models.Model):
    """
    Tracks user's daily activity streak.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak',
        verbose_name='User'
    )
    
    current_streak = models.IntegerField(
        default=0,
        verbose_name='Current Streak',
        help_text='Current consecutive days of activity'
    )
    
    longest_streak = models.IntegerField(
        default=0,
        verbose_name='Longest Streak',
        help_text='Longest streak ever achieved'
    )
    
    last_activity_date = models.DateField(
        default=date.today,
        verbose_name='Last Activity Date'
    )
    
    class Meta:
        db_table = 'daily_streaks'
        verbose_name = 'Daily Streak'
        verbose_name_plural = 'Daily Streaks'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_streak} days"
    
    def update_streak(self):
        """Update streak based on current date"""
        today = date.today()
        
        if self.last_activity_date == today:
            # Already counted today
            return False
        
        yesterday = today - timedelta(days=1)
        
        if self.last_activity_date == yesterday:
            # Continue streak
            self.current_streak += 1
        elif self.last_activity_date < yesterday:
            # Streak broken, reset
            self.current_streak = 1
        
        # Update longest streak
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_activity_date = today
        self.save()
        return True


class Challenge(models.Model):
    """
    Represents a daily or weekly challenge.
    """
    CHALLENGE_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    TARGET_METRICS = [
        ('exercises_solved', 'Exercises Solved'),
        ('lessons_completed', 'Lessons Completed'),
        ('xp_earned', 'XP Earned'),
        ('code_submissions', 'Code Submissions'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Title'
    )
    
    description = models.TextField(
        verbose_name='Description'
    )
    
    challenge_type = models.CharField(
        max_length=20,
        choices=CHALLENGE_TYPES,
        verbose_name='Challenge Type'
    )
    
    start_date = models.DateField(
        verbose_name='Start Date'
    )
    
    end_date = models.DateField(
        verbose_name='End Date'
    )
    
    target_metric = models.CharField(
        max_length=50,
        choices=TARGET_METRICS,
        verbose_name='Target Metric'
    )
    
    target_value = models.IntegerField(
        verbose_name='Target Value',
        help_text='Goal to achieve'
    )
    
    xp_reward = models.IntegerField(
        default=100,
        verbose_name='XP Reward'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active'
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created At'
    )
    
    class Meta:
        db_table = 'challenges'
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['challenge_type', 'is_active', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.challenge_type})"
    
    def is_expired(self):
        """Check if challenge has expired"""
        return date.today() > self.end_date


class UserChallenge(models.Model):
    """
    Tracks user progress on challenges.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='challenges',
        verbose_name='User'
    )
    
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Challenge'
    )
    
    progress = models.IntegerField(
        default=0,
        verbose_name='Progress',
        help_text='Current progress toward goal'
    )
    
    completed = models.BooleanField(
        default=False,
        verbose_name='Completed'
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Completed At'
    )
    
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Started At'
    )
    
    class Meta:
        db_table = 'user_challenges'
        verbose_name = 'User Challenge'
        verbose_name_plural = 'User Challenges'
        unique_together = ['user', 'challenge']
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'completed']),
        ]
    
    def __str__(self):
        status = "✓" if self.completed else f"{self.progress}/{self.challenge.target_value}"
        return f"{self.user.username} - {self.challenge.title} ({status})"
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.challenge.target_value == 0:
            return 100
        return min(100, int((self.progress / self.challenge.target_value) * 100))
    
    def check_completion(self):
        """Check if challenge is completed"""
        if not self.completed and self.progress >= self.challenge.target_value:
            self.completed = True
            self.completed_at = timezone.now()
            self.save()
            return True
        return False


class Friendship(models.Model):
    """
    Represents friendship connections between users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friendships',
        verbose_name='User'
    )
    
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='friend_requests',
        verbose_name='Friend'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created At'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        db_table = 'friendships'
        verbose_name = 'Friendship'
        verbose_name_plural = 'Friendships'
        unique_together = ['user', 'friend']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['friend', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.friend.username} ({self.status})"
