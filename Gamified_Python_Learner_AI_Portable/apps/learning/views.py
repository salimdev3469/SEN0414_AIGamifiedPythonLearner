from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Module, Lesson, UserProgress


def curriculum_view(request):
    """Display all modules and lessons (curriculum overview)"""
    modules = Module.objects.filter(is_published=True).prefetch_related(
        'lessons'
    ).order_by('order')
    
    # Calculate progress and completion status for authenticated users
    if request.user.is_authenticated:
        for module in modules:
            module.completion = module.get_completion_percentage(request.user)
            # Add completion status to each lesson
            lessons = list(module.lessons.filter(is_published=True).order_by('order'))
            for lesson in lessons:
                lesson.is_completed = lesson.is_completed_by(request.user)
            # Cache the lessons list with completion status
            module.lessons_with_status = lessons
    else:
        # For non-authenticated users, just get published lessons
        for module in modules:
            lessons = list(module.lessons.filter(is_published=True).order_by('order'))
            for lesson in lessons:
                lesson.is_completed = False
            module.lessons_with_status = lessons
    
    context = {
        'modules': modules,
    }
    
    return render(request, 'learning/curriculum.html', context)


@login_required
def lesson_detail_view(request, lesson_id):
    """Display a specific lesson with content"""
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    
    # Get or create progress entry
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'status': 'not_started'}
    )
    
    # Mark as in progress if not started
    if progress.status == 'not_started':
        progress.mark_in_progress()
    
    # Get adjacent lessons
    next_lesson = lesson.get_next_lesson()
    previous_lesson = lesson.get_previous_lesson()
    
    # Check if lesson is completed
    is_completed = progress.status == 'completed'
    
    context = {
        'lesson': lesson,
        'module': lesson.module,
        'progress': progress,
        'is_completed': is_completed,
        'next_lesson': next_lesson,
        'previous_lesson': previous_lesson,
    }
    
    return render(request, 'learning/lesson_detail.html', context)


@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed and award XP"""
    if request.method != 'POST':
        return redirect('learning:lesson_detail', lesson_id=lesson_id)
    
    lesson = get_object_or_404(Lesson, id=lesson_id, is_published=True)
    
    # Get or create progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'status': 'not_started'}
    )
    
    # Mark as completed
    if progress.mark_completed():
        messages.success(
            request,
            f'🎉 Congratulations! You completed "{lesson.title}" and earned {lesson.xp_reward} XP!'
        )
        
        # Update streak
        from apps.gamification.streak_manager import update_user_streak
        update_user_streak(request.user)
        
        # Check and award badges
        from apps.gamification.badge_engine import check_badges
        newly_earned_badges = check_badges(request.user)
        
        # Show badge notifications
        for badge in newly_earned_badges:
            messages.success(request, f'🏆 New Badge Earned: {badge.icon} {badge.name} (+{badge.xp_reward} XP)')
        
        # Update challenges
        from apps.gamification.challenge_manager import update_challenge
        update_challenge(request.user, 'lessons_completed', 1)
    else:
        messages.info(request, 'You have already completed this lesson.')
    
    # Check if user leveled up
    if request.user.xp >= request.user.xp_for_next_level():
        messages.success(request, f'🎊 Level Up! You are now Level {request.user.level}!')
    
    # Redirect to next lesson or back to current lesson
    next_lesson = lesson.get_next_lesson()
    if next_lesson:
        return redirect('learning:lesson_detail', lesson_id=next_lesson.id)
    else:
        messages.success(request, '🏆 Awesome! You completed all lessons in this module!')
        return redirect('learning:curriculum')


@login_required
def module_detail_view(request, module_id):
    """Display all lessons in a module"""
    module = get_object_or_404(Module, id=module_id, is_published=True)
    lessons = module.get_lessons()
    
    # Add completion status to each lesson
    for lesson in lessons:
        lesson.is_completed = lesson.is_completed_by(request.user)
    
    completion_percentage = module.get_completion_percentage(request.user)
    
    context = {
        'module': module,
        'lessons': lessons,
        'completion_percentage': completion_percentage,
    }
    
    return render(request, 'learning/module_detail.html', context)
