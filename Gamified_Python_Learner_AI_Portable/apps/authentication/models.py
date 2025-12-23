from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model with gamification features
    Extends Django's AbstractUser to add XP, level, and other game mechanics
    """
    
    # Gamification Fields
    xp = models.IntegerField(
        default=0,
        verbose_name="Experience Points",
        help_text="Total XP earned by the user"
    )
    
    level = models.IntegerField(
        default=1,
        verbose_name="User Level",
        help_text="Current level based on XP"
    )
    
    # Profile Fields
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Profile Avatar"
    )
    
    bio = models.TextField(
        blank=True,
        max_length=500,
        verbose_name="Biography",
        help_text="Short bio about the user"
    )
    
    # Tracking Fields
    date_joined = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Statistics
    total_exercises_completed = models.IntegerField(default=0)
    total_lessons_completed = models.IntegerField(default=0)
    current_streak = models.IntegerField(
        default=0,
        help_text="Consecutive days of activity"
    )
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-xp', '-level']
    
    def __str__(self):
        return f"{self.username} (Level {self.level}, {self.xp} XP)"
    
    def add_xp(self, amount):
        """Add XP and check for level up"""
        self.xp += amount
        self.check_level_up()
        self.save()
    
    def check_level_up(self):
        """Check if user should level up based on XP"""
        from django.conf import settings
        
        base_xp = settings.XP_FOR_LEVEL_UP_BASE
        multiplier = settings.XP_MULTIPLIER_PER_LEVEL
        
        # Calculate cumulative XP required for current level
        # Level 1: 0 XP
        # Level 2: base_xp XP (1000)
        # Level 3: base_xp + base_xp * multiplier XP (1000 + 1500 = 2500)
        # Level 4: base_xp + base_xp * multiplier + base_xp * multiplier^2 XP (1000 + 1500 + 2250 = 4750)
        
        # Calculate cumulative XP required for next level
        cumulative_xp_required = 0
        for i in range(self.level):
            cumulative_xp_required += base_xp * (multiplier ** i)
        
        # Keep leveling up while XP is sufficient
        while self.xp >= cumulative_xp_required:
            self.level += 1
            cumulative_xp_required += base_xp * (multiplier ** (self.level - 1))
    
    def xp_for_next_level(self):
        """Calculate cumulative XP needed for next level"""
        from django.conf import settings
        
        base_xp = settings.XP_FOR_LEVEL_UP_BASE
        multiplier = settings.XP_MULTIPLIER_PER_LEVEL
        
        # Calculate cumulative XP required for next level
        cumulative_xp = 0
        for i in range(self.level):
            cumulative_xp += base_xp * (multiplier ** i)
        
        return int(cumulative_xp)
    
    def xp_progress_percentage(self):
        """Calculate progress percentage to next level"""
        from django.conf import settings
        
        base_xp = settings.XP_FOR_LEVEL_UP_BASE
        multiplier = settings.XP_MULTIPLIER_PER_LEVEL
        
        # Calculate cumulative XP required for current level
        current_level_xp = 0
        for i in range(self.level - 1):
            current_level_xp += base_xp * (multiplier ** i)
        
        # Calculate cumulative XP required for next level
        next_level_xp = current_level_xp + base_xp * (multiplier ** (self.level - 1))
        
        # Calculate progress
        current_progress = self.xp - current_level_xp
        level_range = next_level_xp - current_level_xp
        
        if level_range <= 0:
            return 100
        
        percentage = int((current_progress / level_range) * 100)
        return max(0, min(100, percentage))  # Clamp between 0 and 100
