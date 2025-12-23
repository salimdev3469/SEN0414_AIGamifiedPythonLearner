"""
Custom SMTP email backend with timeout support
"""
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class TimeoutSMTPEmailBackend(SMTPEmailBackend):
    """
    Custom SMTP backend with configurable timeout and better error logging
    """
    def __init__(self, host=None, port=None, username=None, password=None,
                 use_tls=None, fail_silently=False, use_ssl=None, timeout=None,
                 ssl_keyfile=None, ssl_certfile=None, **kwargs):
        # Get timeout from settings if not provided
        if timeout is None:
            timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
        
        # Log email backend initialization
        logger.info(f"Initializing SMTP backend - Host: {host or getattr(settings, 'EMAIL_HOST', 'NOT SET')}, "
                   f"Port: {port or getattr(settings, 'EMAIL_PORT', 'NOT SET')}, "
                   f"Username: {'SET' if (username or getattr(settings, 'EMAIL_HOST_USER', '')) else 'NOT SET'}, "
                   f"Timeout: {timeout}")
        
        super().__init__(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=use_tls,
            fail_silently=fail_silently,
            use_ssl=use_ssl,
            timeout=timeout,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
            **kwargs
        )
    
    def open(self):
        """
        Override open to add connection logging
        """
        try:
            result = super().open()
            logger.info(f"SMTP connection opened successfully to {self.host}:{self.port}")
            return result
        except Exception as e:
            logger.error(f"Failed to open SMTP connection to {self.host}:{self.port}: {type(e).__name__}: {e}", exc_info=True)
            raise
    
    def send_messages(self, email_messages):
        """
        Override send_messages to add better error logging
        """
        if not email_messages:
            return 0
        
        # Log email details
        for msg in email_messages:
            logger.info(f"Attempting to send email - From: {msg.from_email}, To: {msg.to}, Subject: {msg.subject}")
        
        try:
            # Ensure connection is open
            if not self.connection:
                self.open()
            
            result = super().send_messages(email_messages)
            logger.info(f"Successfully sent {result} email message(s) via SMTP")
            return result
        except Exception as e:
            logger.error(f"Failed to send email messages: {type(e).__name__}: {e}", exc_info=True)
            logger.error(f"SMTP connection state - Host: {self.host}, Port: {self.port}, Username: {self.username}")
            raise

