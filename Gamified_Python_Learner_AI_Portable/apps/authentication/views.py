from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.db import models
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CustomPasswordChangeForm, EmailChangeForm
from .models import User


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Use the first authentication backend for login
            from django.conf import settings
            backend = settings.AUTHENTICATION_BACKENDS[0] if settings.AUTHENTICATION_BACKENDS else None
            login(request, user, backend=backend)
            messages.success(request, f'Welcome {user.username}! Your account has been created successfully.')
            return redirect('auth:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('auth:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # authenticate() will try both username and email with our custom backend
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next page if specified, otherwise dashboard
                next_page = request.GET.get('next', 'auth:dashboard')
                return redirect(next_page)
        else:
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """User dashboard view"""
    user = request.user
    
    # Calculate progress to next level
    xp_needed = user.xp_for_next_level()
    xp_progress = user.xp_progress_percentage()
    
    # Get recent badges (to be implemented when gamification app is ready)
    recent_badges = []
    
    context = {
        'user': user,
        'xp_needed': xp_needed,
        'xp_progress': xp_progress,
        'recent_badges': recent_badges,
    }
    
    return render(request, 'authentication/dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('auth:profile')
    else:
        form = UserProfileForm(instance=user)
    
    # Calculate stats
    xp_needed = user.xp_for_next_level()
    xp_progress = user.xp_progress_percentage()
    
    context = {
        'form': form,
        'user': user,
        'xp_needed': xp_needed,
        'xp_progress': xp_progress,
    }
    
    return render(request, 'authentication/profile.html', context)


@login_required
def leaderboard_view(request):
    """Leaderboard view showing top users"""
    # Get top users ordered by XP
    top_users = User.objects.all().order_by('-xp', '-level')[:50]
    
    # Ensure levels are up to date for displayed users and current user
    users_to_check = list(top_users) + [request.user]
    for user in users_to_check:
        old_level = user.level
        user.check_level_up()
        if user.level != old_level:
            user.save()
    
    # Refresh top_users after level updates
    top_users = User.objects.all().order_by('-xp', '-level')[:50]
    
    # Ensure current user's level is up to date for rank calculation
    request.user.refresh_from_db()
    
    # Find current user's rank (users with more XP, or same XP but higher level)
    user_rank = User.objects.filter(
        models.Q(xp__gt=request.user.xp) | 
        models.Q(xp=request.user.xp, level__gt=request.user.level)
    ).count() + 1
    
    context = {
        'top_users': top_users,
        'user_rank': user_rank,
    }
    
    return render(request, 'authentication/leaderboard.html', context)


@login_required
def password_change_view(request):
    """Password change view for logged-in users"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to prevent logout after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('auth:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'authentication/password_change.html', {'form': form})


@login_required
def email_change_view(request):
    """Email change view for logged-in users"""
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your email address has been changed successfully!')
            return redirect('auth:profile')
    else:
        form = EmailChangeForm(request.user)
    
    return render(request, 'authentication/email_change.html', {'form': form})


@login_required
def test_email_view(request):
    """Test email sending (for debugging)"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.http import JsonResponse
    
    if request.method == 'POST':
        test_email = request.POST.get('email', request.user.email)
        try:
            send_mail(
                'Test Email from Python Learner AI',
                'This is a test email to verify email configuration.',
                settings.DEFAULT_FROM_EMAIL,
                [test_email],
                fail_silently=False,
            )
            return JsonResponse({'success': True, 'message': f'Test email sent to {test_email}'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Show email configuration status
    email_config = {
        'backend': settings.EMAIL_BACKEND,
        'host': getattr(settings, 'EMAIL_HOST', 'N/A'),
        'port': getattr(settings, 'EMAIL_PORT', 'N/A'),
        'use_tls': getattr(settings, 'EMAIL_USE_TLS', False),
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'has_credentials': bool(getattr(settings, 'EMAIL_HOST_USER', '')),
    }
    
    return JsonResponse(email_config)
