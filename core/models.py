from django.db import models
from django.contrib.auth import get_user_model

User=get_user_model()

# Create your models here.

class Skill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    organization = models.CharField(max_length=150, blank=True, help_text="College, company, startup, etc.")
    location = models.CharField(max_length=100, blank=True)
    EXPERIENCE_CHOICES = [
        ("student", "Student"),
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("professional", "Professional"),
    ]
    skills = models.ManyToManyField(Skill,blank=True, related_name="profiles")
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default="student")  
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
class Project(models.Model):
    author=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="projects")
    title=models.CharField(max_length=100)
    description=models.TextField(max_length=500)
    screenshot = models.ImageField(upload_to='project_snips/', blank=True, null=True)
    github_url = models.URLField(blank=True)
    live_demo_url = models.URLField(blank=True)
    technologies=models.ManyToManyField(Skill, blank=True, related_name="projects")
    CATEGORY_CHOICES = [
        ("web", "Web Development"),
        ("mobile", "Mobile App"),
        ("desktop", "Desktop Application"),
        ("ai_ml", "AI / Machine Learning"),
        ("data_science", "Data Science"),
        ("game", "Game Development"),
        ("api", "API / Backend"),
        ("other", "Other"),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,default="web")
    tags = models.CharField(max_length=200,blank=True,help_text="Separate tags with commas")
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-published_at"]
    def __str__(self):
        return self.title
    
class Like(models.Model):
    user=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    project=models.ForeignKey(Project,on_delete=models.CASCADE, related_name="likes")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints= [
            models.UniqueConstraint(fields=["user","project"],name="unique_project_like")
        ]
    def __str__(self):
        return f"{self.user.user.username} liked {self.project.title}"

class Comment(models.Model):
    author = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="comments")
    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name="comments")
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]
    def __str__(self):
        return f"{self.author.user.username} on {self.project.title}"
    
class Bookmark(models.Model):
    user=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="bookmarks")
    project=models.ForeignKey(Project,on_delete=models.CASCADE, related_name="bookmarks")
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints= [
            models.UniqueConstraint(fields=["user","project"],name="unique_project_bookmark")
        ]
    def __str__(self):
        return f"{self.user.user.username} bookmarked {self.project.title}"
    
