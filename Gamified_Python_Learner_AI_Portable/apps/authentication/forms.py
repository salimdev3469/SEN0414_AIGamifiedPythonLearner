from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Custom registration form with additional fields"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email'
        })
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Choose a username'
        })
    )
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Create a password (min 8 characters)'
        })
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your password'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled inputs"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username or Email'
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form with styled inputs"""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your current password'
        })
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password (min 8 characters)'
        })
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password'
        })
    )


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with styled email input"""
    
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })
    )


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with styled password inputs"""
    
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password'
        }),
        help_text='Your password must contain at least 8 characters.'
    )
    
    new_password2 = forms.CharField(
        label='New password confirmation',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password'
        }),
        help_text='Enter the same password as before, for verification.'
    )


class EmailChangeForm(forms.Form):
    """Form for changing user email"""
    
    new_email = forms.EmailField(
        label='New Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your new email address'
        })
    )
    
    password = forms.CharField(
        label='Current Password',
        help_text='Enter your current password to confirm the email change',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your current password'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        if new_email == self.user.email:
            raise forms.ValidationError('This is already your current email address.')
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError('This email is already registered by another user.')
        return new_email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not self.user.check_password(password):
            raise forms.ValidationError('Incorrect password. Please enter your current password.')
        return password
    
    def save(self):
        """Update user email"""
        self.user.email = self.cleaned_data['new_email']
        self.user.save()
        return self.user

