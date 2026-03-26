from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return cleaned_data
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user'] # We don't want the user to change the linked account
        widgets = {
            'skills': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'e.g., Python, SQL, Project Management, Public Speaking'
            }),
            'career_goals': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'e.g., I want to become a Senior Data Scientist in the healthcare sector within 5 years.'
            }),
            'github_profile': forms.URLInput(attrs={'placeholder': 'https://github.com/yourusername'}),
            'linkedin_profile': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/yourusername'}),
            'portfolio_website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }
