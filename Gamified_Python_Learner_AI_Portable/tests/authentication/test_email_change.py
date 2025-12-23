"""
Unit tests for email change functionality
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.authentication.models import User

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailChangeView:
    """Test email change view"""
    
    def test_email_change_requires_login(self, client):
        """Test email change requires authentication"""
        response = client.get(reverse('auth:email_change'))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_email_change_page_loads(self, authenticated_client, test_user):
        """Test email change page loads for authenticated user"""
        response = authenticated_client.get(reverse('auth:email_change'))
        assert response.status_code == 200
        assert 'form' in response.context
        assert 'user' in response.context
        assert response.context['user'] == test_user
    
    def test_email_change_success(self, authenticated_client, test_user):
        """Test successful email change"""
        old_email = test_user.email
        new_email = 'newemail@example.com'
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': new_email,
            'password': 'TestPass123!',
        })
        
        # Should redirect to profile on success
        assert response.status_code == 302
        assert 'profile' in response.url
        
        # Verify email was changed
        test_user.refresh_from_db()
        assert test_user.email == new_email
        assert test_user.email != old_email
    
    def test_email_change_wrong_password(self, authenticated_client, test_user):
        """Test email change fails with wrong password"""
        old_email = test_user.email
        new_email = 'newemail@example.com'
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': new_email,
            'password': 'WrongPassword123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Email should not be changed
        test_user.refresh_from_db()
        assert test_user.email == old_email
    
    def test_email_change_same_email(self, authenticated_client, test_user):
        """Test email change fails when new email is same as current"""
        old_email = test_user.email
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': old_email,
            'password': 'TestPass123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Email should not be changed
        test_user.refresh_from_db()
        assert test_user.email == old_email
    
    def test_email_change_duplicate_email(self, authenticated_client, test_user, db):
        """Test email change fails when email is already used by another user"""
        # Create another user with different email
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        
        # Try to change email to other user's email
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': other_user.email,
            'password': 'TestPass123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Email should not be changed
        test_user.refresh_from_db()
        assert test_user.email != other_user.email
    
    def test_email_change_invalid_email_format(self, authenticated_client, test_user):
        """Test email change fails with invalid email format"""
        old_email = test_user.email
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': 'not-an-email',
            'password': 'TestPass123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Email should not be changed
        test_user.refresh_from_db()
        assert test_user.email == old_email
    
    def test_email_change_requires_password(self, authenticated_client, test_user):
        """Test email change requires password"""
        old_email = test_user.email
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': 'newemail@example.com',
            # Missing password
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Email should not be changed
        test_user.refresh_from_db()
        assert test_user.email == old_email


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailChangeForm:
    """Test email change form validation"""
    
    def test_email_change_form_fields(self, authenticated_client):
        """Test email change form has required fields"""
        response = authenticated_client.get(reverse('auth:email_change'))
        form = response.context['form']
        
        assert 'new_email' in form.fields
        assert 'password' in form.fields
    
    def test_email_change_form_shows_current_email(self, authenticated_client, test_user):
        """Test email change page shows current email"""
        response = authenticated_client.get(reverse('auth:email_change'))
        assert response.status_code == 200
        # Check that current email is displayed in template context
        assert 'user' in response.context
        assert response.context['user'].email == test_user.email


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailChangeIntegration:
    """Integration tests for email change"""
    
    def test_email_change_allows_same_user_different_case(self, authenticated_client, test_user):
        """Test that email change works (case sensitivity handled by Django)"""
        # Django's User model is case-insensitive for email by default
        # This test verifies the form allows changing email
        new_email = 'NEWEMAIL@EXAMPLE.COM'
        
        response = authenticated_client.post(reverse('auth:email_change'), {
            'new_email': new_email,
            'password': 'TestPass123!',
        })
        
        # Should succeed (Django normalizes email to lowercase)
        assert response.status_code == 302
        
        # Verify email was changed (should be lowercase)
        test_user.refresh_from_db()
        assert test_user.email.lower() == new_email.lower()

