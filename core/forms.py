from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Project, Profile, Comment

User = get_user_model()

class SignUpForm(UserCreationForm):
    email=forms.EmailField(required=True)
    class Meta:
        model=User
        fields=[
            "username",
            "email",
            "password1",
            "password2",
        ]   

class ProjectForm(forms.ModelForm):
    class Meta:
        model=Project
        fields= [
            "title", 
            "description", 
            "screenshot", 
            "github_url", 
            "live_demo_url", 
            "technologies", 
            "category", 
            "tags",
        ]

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields= [
            "profile_picture",
            "bio",
            "organization",
            "location",
            "experience_level",
            "skills",
            "github_url",
            "linkedin_url",
            "portfolio_url",
        ]

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields= [
            "content",
        ]
        widgets = {
            "content": forms.Textarea(attrs={
                "id": "comment-input",
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write a comment..."
            })
        }