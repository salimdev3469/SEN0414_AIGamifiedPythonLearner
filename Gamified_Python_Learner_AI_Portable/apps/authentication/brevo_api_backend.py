"""
Brevo HTTP API email backend
Uses Brevo's REST API instead of SMTP for more reliable email delivery
"""
from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import logging
import requests
import json

logger = logging.getLogger(__name__)


class BrevoAPIEmailBackend(BaseEmailBackend):
    """
    Email backend using Brevo HTTP API
    More reliable than SMTP, especially on platforms like Render
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = getattr(settings, 'BREVO_API_KEY', None)
        self.api_url = 'https://api.brevo.com/v3/smtp/email'
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'pythonlearnerai@gmail.com')
        self.from_name = getattr(settings, 'EMAIL_FROM_NAME', 'Python Learner AI')
        
        if not self.api_key:
            logger.warning("BREVO_API_KEY not set - email sending will fail")
    
    def send_messages(self, email_messages):
        """
        Send email messages using Brevo HTTP API
        """
        if not email_messages:
            return 0
        
        if not self.api_key:
            if not self.fail_silently:
                raise ValueError("BREVO_API_KEY is not configured")
            return 0
        
        success_count = 0
        
        for message in email_messages:
            try:
                # Prepare email data for Brevo API
                email_data = {
                    'sender': {
                        'email': message.from_email or self.from_email,
                        'name': self.from_name
                    },
                    'to': [{'email': email} for email in message.to],
                    'subject': message.subject,
                }
                
                # Add CC if present
                if message.cc:
                    email_data['cc'] = [{'email': email} for email in message.cc]
                
                # Add BCC if present
                if message.bcc:
                    email_data['bcc'] = [{'email': email} for email in message.bcc]
                
                # Add reply-to if present
                if message.reply_to:
                    email_data['replyTo'] = {'email': message.reply_to[0]}
                
                # Add email content
                if message.body:
                    # If message has HTML alternative, use it
                    if hasattr(message, 'alternatives') and message.alternatives:
                        for content, mimetype in message.alternatives:
                            if mimetype == 'text/html':
                                email_data['htmlContent'] = content
                                break
                        # If no HTML found, use plain text
                        if 'htmlContent' not in email_data:
                            email_data['textContent'] = message.body
                    else:
                        # Plain text email
                        email_data['textContent'] = message.body
                
                # Log email attempt
                logger.info(f"Sending email via Brevo API - To: {message.to}, Subject: {message.subject}")
                
                # Send email via Brevo API
                headers = {
                    'api-key': self.api_key,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=email_data,
                    timeout=30  # 30 seconds timeout
                )
                
                # Check response
                if response.status_code == 201:
                    logger.info(f"Email sent successfully via Brevo API - Message ID: {response.json().get('messageId', 'unknown')}")
                    success_count += 1
                else:
                    error_msg = f"Brevo API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    if not self.fail_silently:
                        raise Exception(error_msg)
                    
            except requests.exceptions.Timeout:
                error_msg = "Brevo API request timed out"
                logger.error(error_msg)
                if not self.fail_silently:
                    raise Exception(error_msg)
            except requests.exceptions.RequestException as e:
                error_msg = f"Brevo API request failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                if not self.fail_silently:
                    raise Exception(error_msg)
            except Exception as e:
                error_msg = f"Error sending email via Brevo API: {type(e).__name__}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                if not self.fail_silently:
                    raise
        
        return success_count

