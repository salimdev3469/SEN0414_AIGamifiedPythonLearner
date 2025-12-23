"""
URL configuration for Gamified Python Learner AI project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home page
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Authentication URLs
    path('', include('apps.authentication.urls', namespace='auth')),
    
    # Learning URLs
    path('', include('apps.learning.urls', namespace='learning')),
    
    # Coding Exercises URLs
    path('', include('apps.coding.urls', namespace='coding')),
    
    # AI Tutor URLs
    path('', include('apps.ai_tutor.urls', namespace='ai_tutor')),
    
    # Gamification URLs
    path('', include('apps.gamification.urls', namespace='gamification')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
