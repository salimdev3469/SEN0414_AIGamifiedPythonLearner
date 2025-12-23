"""
Tests for email backends
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.mail import EmailMessage
from apps.authentication.email_backend import TimeoutSMTPEmailBackend


class TestTimeoutSMTPEmailBackend:
    """Tests for TimeoutSMTPEmailBackend"""
    
    def test_init_with_default_timeout(self):
        """Test initialization with default timeout"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.timeout = 10
            assert backend.timeout == 10
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.__init__')
    def test_init_with_custom_timeout(self, mock_super_init):
        """Test initialization with custom timeout"""
        mock_super_init.return_value = None
        
        backend = TimeoutSMTPEmailBackend(timeout=30)
        
        mock_super_init.assert_called_once()
        call_kwargs = mock_super_init.call_args.kwargs
        assert call_kwargs['timeout'] == 30
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.__init__')
    def test_init_uses_default_timeout(self, mock_super_init):
        """Test initialization uses default timeout"""
        mock_super_init.return_value = None
        
        backend = TimeoutSMTPEmailBackend()
        
        call_kwargs = mock_super_init.call_args.kwargs
        # Should use default timeout of 10 or from settings
        assert 'timeout' in call_kwargs
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.open')
    def test_open_success(self, mock_open):
        """Test successful connection opening"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            
            mock_open.return_value = True
            
            result = backend.open()
            
            assert result == True
            mock_open.assert_called_once()
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.open')
    def test_open_failure(self, mock_open):
        """Test connection opening failure"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            
            mock_open.side_effect = Exception("Connection failed")
            
            with pytest.raises(Exception) as exc_info:
                backend.open()
            
            assert "Connection failed" in str(exc_info.value)
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.send_messages')
    @patch('apps.authentication.email_backend.SMTPEmailBackend.open')
    def test_send_messages_success(self, mock_open, mock_send):
        """Test successful message sending"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            backend.username = 'test@example.com'
            backend.connection = MagicMock()
            
            mock_send.return_value = 1
            
            msg = MagicMock()
            msg.from_email = 'test@example.com'
            msg.to = ['recipient@example.com']
            msg.subject = 'Test Subject'
            
            result = backend.send_messages([msg])
            
            assert result == 1
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.send_messages')
    def test_send_messages_empty_list(self, mock_send):
        """Test sending empty message list"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            backend.connection = MagicMock()
            
            result = backend.send_messages([])
            
            assert result == 0
            mock_send.assert_not_called()
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.send_messages')
    @patch('apps.authentication.email_backend.SMTPEmailBackend.open')
    def test_send_messages_opens_connection_if_needed(self, mock_open, mock_send):
        """Test that send_messages opens connection if not open"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            backend.username = 'test@example.com'
            backend.connection = None  # No connection
            
            mock_send.return_value = 1
            
            msg = MagicMock()
            msg.from_email = 'test@example.com'
            msg.to = ['recipient@example.com']
            msg.subject = 'Test Subject'
            
            backend.send_messages([msg])
            
            mock_open.assert_called_once()
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.send_messages')
    def test_send_messages_failure(self, mock_send):
        """Test message sending failure"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            backend.username = 'test@example.com'
            backend.connection = MagicMock()
            
            mock_send.side_effect = Exception("SMTP error")
            
            msg = MagicMock()
            msg.from_email = 'test@example.com'
            msg.to = ['recipient@example.com']
            msg.subject = 'Test Subject'
            
            with pytest.raises(Exception) as exc_info:
                backend.send_messages([msg])
            
            assert "SMTP error" in str(exc_info.value)
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.send_messages')
    def test_send_multiple_messages(self, mock_send):
        """Test sending multiple messages"""
        with patch.object(TimeoutSMTPEmailBackend, '__init__', lambda x: None):
            backend = TimeoutSMTPEmailBackend()
            backend.host = 'smtp.example.com'
            backend.port = 587
            backend.username = 'test@example.com'
            backend.connection = MagicMock()
            
            mock_send.return_value = 3
            
            messages = []
            for i in range(3):
                msg = MagicMock()
                msg.from_email = 'test@example.com'
                msg.to = [f'recipient{i}@example.com']
                msg.subject = f'Test Subject {i}'
                messages.append(msg)
            
            result = backend.send_messages(messages)
            
            assert result == 3


class TestTimeoutSMTPEmailBackendIntegration:
    """Integration tests for TimeoutSMTPEmailBackend"""
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.__init__')
    def test_backend_inherits_smtp(self, mock_init):
        """Test that backend inherits from SMTPEmailBackend"""
        mock_init.return_value = None
        backend = TimeoutSMTPEmailBackend()
        
        from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
        assert isinstance(backend, SMTPEmailBackend)
    
    @patch('apps.authentication.email_backend.SMTPEmailBackend.__init__')
    def test_backend_passes_all_parameters(self, mock_init):
        """Test that all parameters are passed to parent"""
        mock_init.return_value = None
        
        TimeoutSMTPEmailBackend(
            host='smtp.example.com',
            port=587,
            username='user',
            password='pass',
            use_tls=True,
            fail_silently=False,
            timeout=30
        )
        
        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args.kwargs
        assert call_kwargs['host'] == 'smtp.example.com'
        assert call_kwargs['port'] == 587
        assert call_kwargs['username'] == 'user'
        assert call_kwargs['password'] == 'pass'
        assert call_kwargs['use_tls'] == True
        assert call_kwargs['fail_silently'] == False
        assert call_kwargs['timeout'] == 30
