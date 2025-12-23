from django.contrib import admin
from .models import Exercise, TestCase, UserSubmission


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ['input_data', 'expected_output', 'is_hidden', 'order']


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'difficulty', 'xp_reward', 'order', 'is_published', 'created_at']
    list_filter = ['difficulty', 'is_published', 'lesson__module']
    search_fields = ['title', 'description', 'lesson__title']
    list_editable = ['order', 'is_published']
    ordering = ['lesson', 'order']
    inlines = [TestCaseInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('lesson', 'title', 'description', 'difficulty', 'xp_reward')
        }),
        ('Code', {
            'fields': ('starter_code', 'solution_code')
        }),
        ('Help & Guidance', {
            'fields': ('hints', 'expected_approach')
        }),
        ('Settings', {
            'fields': ('order', 'is_published')
        }),
    )


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['exercise', 'order', 'is_hidden', 'input_data_preview']
    list_filter = ['is_hidden', 'exercise__lesson']
    search_fields = ['exercise__title']
    list_editable = ['order', 'is_hidden']
    ordering = ['exercise', 'order']
    
    def input_data_preview(self, obj):
        return obj.input_data[:50] + '...' if len(obj.input_data) > 50 else obj.input_data
    input_data_preview.short_description = 'Input Data'


class UserSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'is_correct', 'test_pass_rate_display', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at', 'exercise__difficulty']
    search_fields = ['user__username', 'exercise__title']
    readonly_fields = ['submitted_at', 'test_pass_rate_display']
    ordering = ['-submitted_at']
    
    def test_pass_rate_display(self, obj):
        return f"{obj.test_pass_rate()}%"
    test_pass_rate_display.short_description = 'Pass Rate'
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('user', 'exercise', 'code', 'submitted_at')
        }),
        ('Results', {
            'fields': ('is_correct', 'passed_tests', 'total_tests', 'test_pass_rate_display', 'execution_time')
        }),
        ('Feedback', {
            'fields': ('feedback', 'suggestions', 'error_message')
        }),
    )


# Register models
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(TestCase, TestCaseAdmin)
admin.site.register(UserSubmission, UserSubmissionAdmin)
