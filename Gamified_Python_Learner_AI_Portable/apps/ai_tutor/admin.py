from django.contrib import admin
from .models import ChatConversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    """Inline admin for chat messages"""
    model = ChatMessage
    extra = 0
    readonly_fields = ['timestamp', 'tokens_used']
    fields = ['role', 'content', 'timestamp', 'tokens_used']
    can_delete = False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    """Admin interface for chat conversations"""
    list_display = ['id', 'user', 'context_type', 'context_id', 'is_active', 'created_at', 'message_count']
    list_filter = ['context_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    def message_count(self, obj):
        return obj.get_message_count()
    message_count.short_description = 'Messages'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages"""
    list_display = ['id', 'conversation', 'role', 'content_preview', 'timestamp', 'tokens_used']
    list_filter = ['role', 'timestamp']
    search_fields = ['content', 'conversation__user__username']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
