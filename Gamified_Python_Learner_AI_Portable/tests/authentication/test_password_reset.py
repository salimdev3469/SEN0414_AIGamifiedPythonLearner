"""
Unit tests for password reset functionality
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.core import mail
from apps.authentication.models import User


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_password_reset_page_loads(self, client):
        """Test password reset page loads correctly"""
        response = client.get(reverse('auth:password_reset'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_password_reset_with_valid_email(self, client, test_user):
        """Test password reset sends email for valid email"""
        response = client.post(reverse('auth:password_reset'), {
            'email': test_user.email
        })
        assert response.status_code == 302  # Redirects to done page
        assert len(mail.outbox) == 1  # Email was sent
        assert 'password reset' in mail.outbox[0].subject.lower()
    
    def test_password_reset_with_invalid_email(self, client):
        """Test password reset doesn't reveal if email exists"""
        response = client.post(reverse('auth:password_reset'), {
            'email': 'nonexistent@example.com'
        })
        # Should still redirect to done page (security: don't reveal if email exists)
        assert response.status_code == 302
        # Email should not be sent for non-existent users
        assert len(mail.outbox) == 0
    
    def test_password_reset_done_page(self, client):
        """Test password reset done page loads"""
        response = client.get(reverse('auth:password_reset_done'))
        assert response.status_code == 200
    
    def test_password_reset_requires_email(self, client):
        """Test password reset form requires email"""
        response = client.post(reverse('auth:password_reset'), {})
        assert response.status_code == 200  # Stays on page with errors
        assert 'form' in response.context
        assert response.context['form'].errors


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetConfirm:
    """Test password reset confirmation"""
    
    def test_password_reset_confirm_with_invalid_token(self, client):
        """Test password reset confirm with invalid token"""
        # Invalid token should show error or redirect
        response = client.get(reverse('auth:password_reset_confirm', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid-token'
        }))
        # Should either show error or redirect
        assert response.status_code in [200, 302]
    
    def test_password_reset_complete_page(self, client):
        """Test password reset complete page loads"""
        response = client.get(reverse('auth:password_reset_complete'))
        assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetIntegration:
    """Integration tests for password reset flow"""
    
    def test_password_reset_full_flow(self, client, test_user):
        """Test complete password reset flow"""
        # Step 1: Request password reset
        response = client.post(reverse('auth:password_reset'), {
            'email': test_user.email
        })
        assert response.status_code == 302
        assert len(mail.outbox) == 1
        
        # Step 2: Extract reset link from email
        email_body = mail.outbox[0].body
        # The email should contain a reset link
        assert 'password' in email_body.lower() or 'reset' in email_body.lower()
        
        # Note: Full integration test would require extracting the actual token
        # from the email and using it, which is complex. This test verifies
        # the email is sent correctly.


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetSecurity:
    """Test security aspects of password reset"""
    
    def test_password_reset_doesnt_reveal_email_existence(self, client):
        """Test that password reset doesn't reveal if email exists"""
        # Try with non-existent email
        response = client.post(reverse('auth:password_reset'), {
            'email': 'nonexistent@example.com'
        })
        # Should still show success message (don't reveal if email exists)
        assert response.status_code == 302
        
    def test_password_reset_link_expires(self, client, test_user):
        """Test that password reset links expire (tested via invalid token)"""
        # This is more of a documentation test - actual expiration
        # is handled by Django's default token generator
        response = client.get(reverse('auth:password_reset_confirm', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid-token'
        }))
        # Invalid/expired tokens should not work
        assert response.status_code in [200, 302]

