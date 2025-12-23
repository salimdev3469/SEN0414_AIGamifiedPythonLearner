from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    # Curriculum overview
    path('curriculum/', views.curriculum_view, name='curriculum'),
    
    # Module detail
    path('module/<int:module_id>/', views.module_detail_view, name='module_detail'),
    
    # Lesson detail
    path('lesson/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail'),
    
    # Mark lesson complete
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_complete'),
]

