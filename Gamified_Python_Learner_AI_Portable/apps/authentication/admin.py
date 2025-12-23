from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with gamification fields"""
    
    list_display = ['username', 'email', 'level', 'xp', 'total_exercises_completed', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'level']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Gamification', {
            'fields': ('xp', 'level', 'total_exercises_completed', 'total_lessons_completed', 'current_streak')
        }),
        ('Profile', {
            'fields': ('avatar', 'bio', 'last_activity')
        }),
    )
    
    readonly_fields = ['last_activity', 'date_joined']
