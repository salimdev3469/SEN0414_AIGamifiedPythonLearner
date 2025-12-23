"""
Custom authentication backend that allows login with either username or email
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to login with either
    their username or email address.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with either username or email
        """
        if username is None:
            username = kwargs.get('username')
        
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username or email
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # If multiple users found, prefer username match
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.filter(email=username).first()
        
        # Check password
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None

