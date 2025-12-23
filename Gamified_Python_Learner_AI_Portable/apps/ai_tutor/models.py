from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatConversation(models.Model):
    """
    Represents a chat conversation between a user and the AI tutor.
    Can be context-aware (linked to a lesson or exercise) or general.
    """
    CONTEXT_TYPES = [
        ('general', 'General'),
        ('lesson', 'Lesson'),
        ('exercise', 'Exercise'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_conversations',
        verbose_name='User'
    )
    
    context_type = models.CharField(
        max_length=20,
        choices=CONTEXT_TYPES,
        default='general',
        verbose_name='Context Type',
        help_text='Type of context for this conversation'
    )
    
    context_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Context ID',
        help_text='ID of the lesson or exercise (if context-aware)'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active',
        help_text='Whether this conversation is currently active'
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
        db_table = 'chat_conversations'
        verbose_name = 'Chat Conversation'
        verbose_name_plural = 'Chat Conversations'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        context_str = f"{self.context_type}"
        if self.context_id:
            context_str += f" #{self.context_id}"
        return f"{self.user.username} - {context_str} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_message_count(self):
        """Get total number of messages in this conversation"""
        return self.messages.count()
    
    def get_last_message(self):
        """Get the last message in this conversation"""
        return self.messages.order_by('-timestamp').first()


class ChatMessage(models.Model):
    """
    Represents a single message in a chat conversation.
    Can be from the user or the AI assistant.
    """
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Conversation'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='Role',
        help_text='Who sent this message'
    )
    
    content = models.TextField(
        verbose_name='Content',
        help_text='Message content'
    )
    
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Timestamp'
    )
    
    tokens_used = models.IntegerField(
        default=0,
        verbose_name='Tokens Used',
        help_text='Number of tokens used for this message (for API tracking)'
    )
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"
