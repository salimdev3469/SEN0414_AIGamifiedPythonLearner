from django.urls import path
from . import views

app_name = 'coding'

urlpatterns = [
    # All exercises overview
    path('exercises/', views.all_exercises_view, name='all_exercises'),
    
    # Exercise list for a lesson
    path('lesson/<int:lesson_id>/exercises/', views.exercise_list_view, name='exercise_list'),
    
    # Exercise detail with code editor
    path('exercise/<int:exercise_id>/', views.exercise_detail_view, name='exercise_detail'),
    
    # Run code (syntax check only, no AI)
    path('exercise/<int:exercise_id>/run/', views.run_code_view, name='run_code'),
    
    # Submit code for evaluation
    path('exercise/<int:exercise_id>/submit/', views.submit_code_view, name='submit_code'),
    
    # Get hint
    path('exercise/<int:exercise_id>/hint/', views.get_hint_view, name='get_hint'),
    
    # Get solution (after 3+ attempts)
    path('exercise/<int:exercise_id>/solution/', views.get_solution_view, name='get_solution'),
]

