from django.db import models
from django.conf import settings
from django.utils import timezone


class Module(models.Model):
    """
    A learning module containing multiple lessons
    Example: "Python Basics", "Functions", "Object-Oriented Programming"
    """
    title = models.CharField(max_length=200, verbose_name="Module Title")
    description = models.TextField(verbose_name="Module Description")
    order = models.IntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Lower numbers appear first"
    )
    icon = models.CharField(
        max_length=50,
        default="📚",
        verbose_name="Module Icon (Emoji)",
        help_text="Emoji to display for this module"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Published",
        help_text="Only published modules are visible to users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['order', 'id']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
    
    def __str__(self):
        return f"{self.icon} {self.title}"
    
    def get_lessons(self):
        """Get all lessons in this module"""
        return self.lessons.filter(is_published=True)
    
    def get_lesson_count(self):
        """Get total number of lessons"""
        return self.lessons.filter(is_published=True).count()
    
    def get_completion_percentage(self, user):
        """Calculate completion percentage for a user"""
        total_lessons = self.get_lesson_count()
        if total_lessons == 0:
            return 0
        
        completed_lessons = UserProgress.objects.filter(
            user=user,
            lesson__module=self,
            status='completed'
        ).count()
        
        return int((completed_lessons / total_lessons) * 100)


class Lesson(models.Model):
    """
    An individual lesson within a module
    """
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Module"
    )
    title = models.CharField(max_length=200, verbose_name="Lesson Title")
    content = models.TextField(
        verbose_name="Lesson Content",
        help_text="Markdown supported"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Display Order",
        help_text="Order within the module"
    )
    xp_reward = models.IntegerField(
        default=100,
        verbose_name="XP Reward",
        help_text="XP awarded when lesson is completed"
    )
    estimated_time = models.IntegerField(
        default=15,
        verbose_name="Estimated Time (minutes)",
        help_text="Estimated time to complete this lesson"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Published"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lessons'
        ordering = ['module', 'order', 'id']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        unique_together = ['module', 'order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"
    
    def is_completed_by(self, user):
        """Check if lesson is completed by user"""
        return UserProgress.objects.filter(
            user=user,
            lesson=self,
            status='completed'
        ).exists()
    
    def get_next_lesson(self):
        """Get the next lesson in the module"""
        try:
            return Lesson.objects.filter(
                module=self.module,
                order__gt=self.order,
                is_published=True
            ).first()
        except Lesson.DoesNotExist:
            return None
    
    def get_previous_lesson(self):
        """Get the previous lesson in the module"""
        try:
            return Lesson.objects.filter(
                module=self.module,
                order__lt=self.order,
                is_published=True
            ).order_by('-order').first()
        except Lesson.DoesNotExist:
            return None


class UserProgress(models.Model):
    """
    Track user progress through lessons
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name="User"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Lesson"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started',
        verbose_name="Status"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'user_progress'
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} ({self.status})"
    
    def mark_completed(self):
        """Mark lesson as completed and award XP"""
        if self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
            self.save()
            
            # Award XP to user
            self.user.add_xp(self.lesson.xp_reward)
            
            # Update user stats
            self.user.total_lessons_completed += 1
            self.user.save()
            
            return True
        return False
    
    def mark_in_progress(self):
        """Mark lesson as in progress"""
        if self.status == 'not_started':
            self.status = 'in_progress'
            self.started_at = timezone.now()
            self.save()
