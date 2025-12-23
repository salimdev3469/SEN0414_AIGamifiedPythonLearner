from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
import json

from .models import Exercise, TestCase, UserSubmission
from apps.learning.models import Lesson, UserProgress, Module
from apps.learning.utils import get_code_evaluator


@login_required
def all_exercises_view(request):
    """
    Display all exercises for lessons that user has completed.
    Shows a nice overview with progress.
    """
    # Get all completed lessons by user (ordered by module and lesson)
    completed_progress = UserProgress.objects.filter(
        user=request.user,
        status='completed'
    ).select_related('lesson__module').order_by('lesson__module__order', 'lesson__order')
    
    # Get lessons with exercises
    lessons_with_exercises = []
    for progress in completed_progress:
        lesson = progress.lesson
        exercises = Exercise.objects.filter(
            lesson=lesson,
            is_published=True
        ).order_by('order')
        
        if exercises.exists():
            # Calculate completion stats
            total_exercises = exercises.count()
            completed_exercises = sum(
                1 for ex in exercises 
                if ex.is_solved_by(request.user)
            )
            
            lessons_with_exercises.append({
                'lesson': lesson,
                'module': lesson.module,
                'total_exercises': total_exercises,
                'completed_exercises': completed_exercises,
                'completion_percentage': int((completed_exercises / total_exercises) * 100) if total_exercises > 0 else 0
            })
    
    context = {
        'lessons_with_exercises': lessons_with_exercises,
        'total_available_lessons': len(lessons_with_exercises),
    }
    
    return render(request, 'coding/all_exercises.html', context)


@login_required
def exercise_list_view(request, lesson_id):
    """
    Display all exercises for a specific lesson.
    User must complete the lesson first.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id)
    module = lesson.module
    
    # Check if user has completed the lesson
    is_lesson_completed = UserProgress.objects.filter(
        user=request.user,
        lesson=lesson,
        status='completed'
    ).exists()
    
    if not is_lesson_completed:
        messages.warning(
            request, 
            f"⚠️ Bu dersi henüz tamamlamadınız! Önce '{lesson.title}' dersini bitirin, sonra egzersizlere başlayabilirsiniz."
        )
        return redirect('learning:lesson_detail', lesson_id=lesson_id)
    
    # Get all published exercises for this lesson
    exercises = Exercise.objects.filter(
        lesson=lesson,
        is_published=True
    ).order_by('order')
    
    # Add completion status for each exercise
    for exercise in exercises:
        exercise.is_solved = exercise.is_solved_by(request.user)
        exercise.attempts = exercise.user_attempts(request.user)
    
    context = {
        'lesson': lesson,
        'module': module,
        'exercises': exercises,
        'total_exercises': exercises.count(),
        'solved_exercises': sum(1 for ex in exercises if ex.is_solved),
    }
    
    return render(request, 'coding/exercise_list.html', context)


@login_required
def exercise_detail_view(request, exercise_id):
    """
    Display exercise detail with code editor.
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)
    lesson = exercise.lesson
    module = lesson.module
    
    # Check if user has completed the lesson
    is_lesson_completed = UserProgress.objects.filter(
        user=request.user,
        lesson=lesson,
        status='completed'
    ).exists()
    
    if not is_lesson_completed:
        messages.warning(
            request, 
            f"⚠️ Bu dersi henüz tamamlamadınız! Önce '{lesson.title}' dersini bitirin, sonra egzersizlere başlayabilirsiniz."
        )
        return redirect('learning:lesson_detail', lesson_id=lesson.id)
    
    # Get user's previous submissions
    previous_submissions = UserSubmission.objects.filter(
        user=request.user,
        exercise=exercise
    ).order_by('-submitted_at')[:5]
    
    # Get test cases (only visible ones for display)
    visible_test_cases = TestCase.objects.filter(
        exercise=exercise,
        is_hidden=False
    ).order_by('order')
    
    # Check if exercise is already solved
    is_solved = exercise.is_solved_by(request.user)
    
    context = {
        'exercise': exercise,
        'lesson': lesson,
        'module': module,
        'previous_submissions': previous_submissions,
        'visible_test_cases': visible_test_cases,
        'is_solved': is_solved,
    }
    
    return render(request, 'coding/exercise_detail.html', context)


@login_required
@require_http_methods(["POST"])
def run_code_view(request, exercise_id):
    """
    Quick syntax check and basic validation (no AI evaluation).
    Returns JSON response with syntax check results.
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    try:
        data = json.loads(request.body)
        user_code = data.get('code', '').strip()
        
        if not user_code:
            return JsonResponse({
                'success': False,
                'error': 'No code provided.'
            }, status=400)
        
        # Basic syntax check
        try:
            compile(user_code, '<string>', 'exec')
            syntax_ok = True
            syntax_error = ""
        except SyntaxError as e:
            syntax_ok = False
            syntax_error = f"Line {e.lineno}: {e.msg}"
        
        if not syntax_ok:
            return JsonResponse({
                'success': True,
                'syntax_ok': False,
                'error_message': syntax_error,
                'message': '❌ Syntax Error Found'
            })
        
        # Execute code and capture output
        import sys
        from io import StringIO
        
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output
        
        execution_error = None
        try:
            # Execute the code in a restricted namespace
            exec_namespace = {}
            exec(user_code, exec_namespace)
            output = redirected_output.getvalue()
        except Exception as e:
            execution_error = f"{type(e).__name__}: {str(e)}"
            output = redirected_output.getvalue()
        finally:
            # Restore stdout
            sys.stdout = old_stdout
        
        if execution_error:
            return JsonResponse({
                'success': True,
                'syntax_ok': True,
                'execution_ok': False,
                'error_message': execution_error,
                'output': output if output else None,
                'message': '❌ Runtime Error'
            })
        
        return JsonResponse({
            'success': True,
            'syntax_ok': True,
            'execution_ok': True,
            'output': output if output else '(No output)',
            'message': '✅ Code executed successfully! Click "Submit" for full evaluation.'
        })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def submit_code_view(request, exercise_id):
    """
    Handle code submission and evaluate using Gemini AI.
    Returns JSON response with evaluation results.
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    # Check if lesson is completed
    is_lesson_completed = UserProgress.objects.filter(
        user=request.user,
        lesson=exercise.lesson,
        status='completed'
    ).exists()
    
    if not is_lesson_completed:
        return JsonResponse({
            'success': False,
            'error': f"⚠️ Bu dersi henüz tamamlamadınız! Önce '{exercise.lesson.title}' dersini bitirin."
        }, status=403)
    
    try:
        # Get submitted code from request
        data = json.loads(request.body)
        user_code = data.get('code', '').strip()
        
        if not user_code:
            return JsonResponse({
                'success': False,
                'error': 'No code provided.'
            }, status=400)
        
        # Get all test cases for this exercise
        test_cases = list(TestCase.objects.filter(exercise=exercise).order_by('order'))
        
        if not test_cases:
            return JsonResponse({
                'success': False,
                'error': 'No test cases available for this exercise.'
            }, status=400)
        
        # Evaluate code using Gemini AI
        evaluator = get_code_evaluator()
        evaluation_result = evaluator.evaluate_submission(
            exercise_description=exercise.description,
            user_code=user_code,
            test_cases=test_cases
        )
        
        # Check if exercise was already solved before creating submission
        was_already_solved = exercise.is_solved_by(request.user)
        
        # Create submission record
        submission = UserSubmission.objects.create(
            user=request.user,
            exercise=exercise,
            code=user_code,
            is_correct=evaluation_result.get('is_correct', False),
            feedback=evaluation_result.get('feedback', ''),
            suggestions=evaluation_result.get('suggestions', ''),
            error_message=evaluation_result.get('error_message', ''),
            passed_tests=evaluation_result.get('passed_tests', 0),
            total_tests=evaluation_result.get('total_tests', len(test_cases)),
        )
        
        # Award XP if correct (and first time solving)
        xp_awarded = 0
        newly_earned_badges = []
        if submission.is_correct and not was_already_solved:
            # This is the first correct submission - award XP
            request.user.add_xp(exercise.xp_reward)
            xp_awarded = exercise.xp_reward
            
            # Update total exercises completed
            request.user.total_exercises_completed += 1
            request.user.save()
            
            # Update streak
            from apps.gamification.streak_manager import update_user_streak
            update_user_streak(request.user)
            
            # Check and award badges
            from apps.gamification.badge_engine import check_badges
            newly_earned_badges = check_badges(request.user)
            
            # Update challenges
            from apps.gamification.challenge_manager import update_challenge
            update_challenge(request.user, 'exercises_solved', 1)
            update_challenge(request.user, 'code_submissions', 1)
        
        return JsonResponse({
            'success': True,
            'is_correct': submission.is_correct,
            'feedback': submission.feedback,
            'suggestions': submission.suggestions,
            'error_message': submission.error_message,
            'passed_tests': submission.passed_tests,
            'total_tests': submission.total_tests,
            'test_results': evaluation_result.get('test_results', []),
            'code_quality_score': evaluation_result.get('code_quality_score', 0),
            'encouragement': evaluation_result.get('encouragement', ''),
            'xp_awarded': xp_awarded,
            'badges_earned': [{'name': badge.name, 'icon': badge.icon, 'xp_reward': badge.xp_reward} for badge in newly_earned_badges] if newly_earned_badges else [],
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid request format.'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_hint_view(request, exercise_id):
    """
    Get next hint for an exercise.
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    hint_index = int(request.GET.get('hint_index', 0))
    hints = exercise.hints or []
    
    if hint_index < len(hints):
        return JsonResponse({
            'success': True,
            'hint': hints[hint_index],
            'hint_index': hint_index,
            'has_more_hints': hint_index + 1 < len(hints)
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No more hints available.'
        }, status=404)


@login_required
@require_http_methods(["GET"])
def get_solution_view(request, exercise_id):
    """
    Get solution code (only after 3+ failed attempts).
    """
    exercise = get_object_or_404(Exercise, id=exercise_id)
    
    attempts = exercise.user_attempts(request.user)
    
    if attempts < 3:
        return JsonResponse({
            'success': False,
            'error': f'You need at least 3 attempts before viewing the solution. Current attempts: {attempts}'
        }, status=403)
    
    return JsonResponse({
        'success': True,
        'solution_code': exercise.solution_code,
        'expected_approach': exercise.expected_approach
    })
