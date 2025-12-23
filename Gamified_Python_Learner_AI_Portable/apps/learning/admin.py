from django.contrib import admin
from .models import Module, Lesson, UserProgress


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['icon', 'title', 'order', 'lesson_count', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['order', 'id']
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Lessons'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'order', 'xp_reward', 'estimated_time', 'is_published']
    list_filter = ['module', 'is_published', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['module', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('module', 'title', 'order', 'is_published')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Rewards & Time', {
            'fields': ('xp_reward', 'estimated_time')
        }),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'status', 'started_at', 'completed_at']
    list_filter = ['status', 'completed_at']
    search_fields = ['user__username', 'lesson__title']
    readonly_fields = ['started_at', 'completed_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'lesson', 'lesson__module')
