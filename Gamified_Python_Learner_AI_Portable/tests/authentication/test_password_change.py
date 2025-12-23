"""
Unit tests for password change functionality
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.authentication.models import User

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordChangeView:
    """Test password change view"""
    
    def test_password_change_requires_login(self, client):
        """Test password change requires authentication"""
        response = client.get(reverse('auth:password_change'))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_password_change_page_loads(self, authenticated_client):
        """Test password change page loads for authenticated user"""
        response = authenticated_client.get(reverse('auth:password_change'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_password_change_success(self, authenticated_client, test_user):
        """Test successful password change"""
        old_password = 'TestPass123!'
        new_password = 'NewPass123!'
        
        # Verify old password works
        assert test_user.check_password(old_password)
        
        # Change password
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': old_password,
            'new_password1': new_password,
            'new_password2': new_password,
        })
        
        # Should redirect to profile on success
        assert response.status_code == 302
        assert 'profile' in response.url
        
        # Verify password was changed
        test_user.refresh_from_db()
        assert test_user.check_password(new_password)
        assert not test_user.check_password(old_password)
    
    def test_password_change_wrong_old_password(self, authenticated_client, test_user):
        """Test password change fails with wrong old password"""
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': 'WrongPassword123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Password should not be changed
        test_user.refresh_from_db()
        assert test_user.check_password('TestPass123!')
    
    def test_password_change_password_mismatch(self, authenticated_client, test_user):
        """Test password change fails when new passwords don't match"""
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': 'TestPass123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'DifferentPass123!',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Password should not be changed
        test_user.refresh_from_db()
        assert test_user.check_password('TestPass123!')
    
    def test_password_change_weak_password(self, authenticated_client, test_user):
        """Test password change fails with weak password"""
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': 'TestPass123!',
            'new_password1': 'short',
            'new_password2': 'short',
        })
        
        # Should stay on page with errors
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors
        
        # Password should not be changed
        test_user.refresh_from_db()
        assert test_user.check_password('TestPass123!')
    
    def test_password_change_session_preserved(self, authenticated_client, test_user):
        """Test that session is preserved after password change"""
        # Change password
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': 'TestPass123!',
            'new_password1': 'NewPass123!',
            'new_password2': 'NewPass123!',
        })
        
        assert response.status_code == 302
        
        # User should still be logged in after password change
        response = authenticated_client.get(reverse('auth:dashboard'))
        assert response.status_code == 200  # Still authenticated


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordChangeForm:
    """Test password change form validation"""
    
    def test_password_change_form_fields(self, authenticated_client):
        """Test password change form has required fields"""
        response = authenticated_client.get(reverse('auth:password_change'))
        form = response.context['form']
        
        assert 'old_password' in form.fields
        assert 'new_password1' in form.fields
        assert 'new_password2' in form.fields
    
    def test_password_change_form_requires_all_fields(self, authenticated_client):
        """Test password change form requires all fields"""
        response = authenticated_client.post(reverse('auth:password_change'), {
            'old_password': 'TestPass123!',
            # Missing new_password1 and new_password2
        })
        
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['form'].errors

