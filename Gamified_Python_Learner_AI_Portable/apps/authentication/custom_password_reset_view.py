"""
Custom password reset view with better error handling
"""
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
import logging
import socket
import smtplib
from socket import timeout as SocketTimeout

logger = logging.getLogger(__name__)


class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Custom password reset view with better error handling for email sending
    """
    template_name = 'authentication/password_reset.html'
    email_template_name = 'authentication/password_reset_email.html'
    subject_template_name = 'authentication/password_reset_email_subject.txt'
    success_url = reverse_lazy('auth:password_reset_done')
    
    def form_valid(self, form):
        """
        Override form_valid to handle email sending errors gracefully
        """
        # Log email configuration for debugging
        logger.info(f"Email config check - EMAIL_HOST_USER: {'SET' if settings.EMAIL_HOST_USER else 'NOT SET'}, "
                   f"EMAIL_HOST_PASSWORD: {'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}, "
                   f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}, "
                   f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'NOT SET')}")
        
        try:
            # Check if email settings are configured
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.error("Email credentials not configured - EMAIL_HOST_USER or EMAIL_HOST_PASSWORD is empty")
                messages.error(
                    self.request,
                    'Email service is not configured. Please contact support.'
                )
                return redirect('auth:password_reset')
            
            # Try to send email with timeout handling
            # Override save to catch email sending errors
            email = form.cleaned_data.get('email', '')
            logger.info(f"Attempting to send password reset email to {email}")
            
            result = super().form_valid(form)
            
            # Check if email was actually sent by checking outbox (for testing) or logs
            logger.info(f"Password reset form processed successfully for {email}")
            return result
            
        except (socket.timeout, TimeoutError, socket.error, smtplib.SMTPException, OSError) as e:
            logger.error(f"SMTP connection error: {type(e).__name__}: {e}", exc_info=True)
            messages.error(
                self.request,
                'Unable to connect to email server (timeout). Please try again later or contact support.'
            )
            return redirect('auth:password_reset')
        except Exception as e:
            logger.error(f"Error sending password reset email: {type(e).__name__}: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            # Log the error but don't expose details to user
            messages.error(
                self.request,
                'An error occurred while sending the password reset email. '
                'Please try again later or contact support.'
            )
            return redirect('auth:password_reset')

