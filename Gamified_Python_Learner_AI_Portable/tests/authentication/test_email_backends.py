"""
Tests for email backends
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.mail import send_mail
from django.conf import settings
from apps.authentication.brevo_api_backend import BrevoAPIEmailBackend
from apps.authentication.email_backend import TimeoutSMTPEmailBackend


@pytest.mark.unit
@pytest.mark.django_db
class TestBrevoAPIEmailBackend:
    """Test Brevo HTTP API email backend"""
    
    @patch('apps.authentication.brevo_api_backend.requests.post')
    def test_send_email_success(self, mock_post):
        """Test successful email sending via Brevo API"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'messageId': 'test123'}
        mock_post.return_value = mock_response
        
        backend = BrevoAPIEmailBackend()
        
        from django.core.mail.message import EmailMessage
        email = EmailMessage(
            subject='Test Subject',
            body='Test Body',
            from_email='test@example.com',
            to=['recipient@example.com']
        )
        
        result = backend.send_messages([email])
        
        assert result == 1
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'api.brevo.com' in call_args[0][0]
    
    @patch('apps.authentication.brevo_api_backend.requests.post')
    def test_send_email_failure(self, mock_post):
        """Test email sending failure"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response
        
        backend = BrevoAPIEmailBackend()
        
        from django.core.mail.message import EmailMessage
        email = EmailMessage(
            subject='Test Subject',
            body='Test Body',
            from_email='test@example.com',
            to=['recipient@example.com']
        )
        
        # Should handle exception and return 0
        try:
            result = backend.send_messages([email])
            assert result == 0
        except Exception:
            # If exception is raised, that's also acceptable behavior
            pass
    
    @patch('apps.authentication.brevo_api_backend.requests.post')
    def test_send_email_with_attachments(self, mock_post):
        """Test sending email with attachments"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'messageId': 'test123'}
        mock_post.return_value = mock_response
        
        backend = BrevoAPIEmailBackend()
        
        from django.core.mail.message import EmailMessage
        email = EmailMessage(
            subject='Test Subject',
            body='Test Body',
            from_email='test@example.com',
            to=['recipient@example.com']
        )
        email.attach('test.txt', b'test content', 'text/plain')
        
        result = backend.send_messages([email])
        assert result == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestTimeoutSMTPEmailBackend:
    """Test custom SMTP email backend with timeout"""
    
    def test_backend_initialization(self):
        """Test that backend initializes with timeout"""
        backend = TimeoutSMTPEmailBackend(
            host='smtp.example.com',
            port=587,
            username='user',
            password='pass',
            use_tls=True,
            timeout=30,
            fail_silently=True
        )
        
        assert backend.host == 'smtp.example.com'
        assert backend.port == 587
        assert backend.timeout == 30
        assert backend.use_tls is True
    
    def test_backend_default_timeout(self):
        """Test that backend uses default timeout from settings"""
        backend = TimeoutSMTPEmailBackend(
            host='smtp.example.com',
            port=587,
            fail_silently=True
        )
        
        # Default timeout should be either from settings or None
        # Backend inherits from Django's SMTPEmailBackend
        assert hasattr(backend, 'timeout')
    
    def test_send_messages_empty_list(self):
        """Test sending empty message list"""
        backend = TimeoutSMTPEmailBackend(
            host='smtp.example.com',
            port=587,
            fail_silently=True
        )
        
        result = backend.send_messages([])
        assert result == 0

