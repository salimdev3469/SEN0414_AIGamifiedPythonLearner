from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm
from .custom_password_reset_view import CustomPasswordResetView

app_name = 'auth'

urlpatterns = [
    # Authentication URLs
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('auth/password-reset/', 
         CustomPasswordResetView.as_view(
             form_class=CustomPasswordResetForm
         ), 
         name='password_reset'),
    path('auth/password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('auth/password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             form_class=CustomSetPasswordForm,
             success_url=reverse_lazy('auth:password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('auth/password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Password Change URL
    path('auth/change-password/', views.password_change_view, name='password_change'),
    
    # Email Change URL
    path('auth/change-email/', views.email_change_view, name='email_change'),
    
    # Email Test URL (for debugging)
    path('auth/test-email/', views.test_email_view, name='test_email'),
    
    # User Dashboard & Profile
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]

