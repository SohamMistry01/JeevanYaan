from django.db import models
from django.contrib.auth.models import User, Group
import os
from jeevanyaan import settings
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    career = models.CharField(max_length=100, blank=True)
    education = models.CharField(max_length=100, blank=True)
    year = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username


def get_module_choices():
    # Construct the path to the 'utils' folder. 
    # Adjust this path if 'utils' is located somewhere else (e.g., inside a specific app folder).
    utils_dir = os.path.join('main', 'utils') 
    excluded_files = ['__init__.py', 'logger.py', 'pdf_generator.py']
    choices = []
    
    try:
        for filename in os.listdir(utils_dir):
            if filename.endswith('.py') and filename not in excluded_files:
                # Remove '.py' for the database value
                module_val = filename.replace('.py', '')
                # Format nicely for the Admin dropdown (e.g., 'notes_assistant' -> 'Notes Assistant')
                display_name = module_val.replace('_', ' ').title()
                choices.append((module_val, display_name))
    except FileNotFoundError:
        # Failsafe in case the folder isn't found during initial setup
        pass
        
    return choices

class ModulesControl(models.Model):
    name_of_module = models.CharField(
        max_length=100, 
        choices=get_module_choices(),
        help_text="Select the tool/module"
    )
    daily_limit = models.PositiveIntegerField(
        default=0, 
        help_text="Maximum number of uses allowed per day"
    )
    role = models.ForeignKey(
        Group, 
        on_delete=models.CASCADE, 
        related_name='module_controls',
        help_text="The user group this limit applies to"
    )

    class Meta:
        verbose_name = 'Modules Control'
        verbose_name_plural = 'Modules Controls'
        # Ensures you don't accidentally assign two different limits to the same module for the same role
        unique_together = ('name_of_module', 'role')

    def __str__(self):
        return f"{self.get_name_of_module_display()} limit for {self.role.name}: {self.daily_limit}"
    
    
class UserModuleUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_usages')
    module_name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'User Module Usage'
        verbose_name_plural = 'User Module Usages'
        # Ensures we only have one record per user, per module, per day
        unique_together = ('user', 'module_name', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.module_name} ({self.date}): {self.usage_count}"
    

class UserProfile(models.Model):
    # Link to standard Django User (handles username, email, password)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # --------------------------------
    # Educational Information
    # --------------------------------
    EDUCATION_CHOICES = [
        ('High School', 'High School'),
        ('Diploma', 'Diploma'),
        ('Bachelors', 'Bachelors Degree'),
        ('Masters', 'Masters Degree'),
        ('PhD', 'PhD / Doctorate'),
        ('Other', 'Other')
    ]
    education_level = models.CharField(max_length=50, choices=EDUCATION_CHOICES, blank=True, null=True)
    degree_name = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., B.Tech in Computer Science")
    
    # --------------------------------
    # Professional Status
    # --------------------------------
    STATUS_CHOICES = [
        ('Student', 'Student'),
        ('Professional', 'Working Professional'),
        ('Job Seeker', 'Seeking Opportunities'),
        ('Freelancer', 'Freelancer')
    ]
    current_status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    primary_domain = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Software Engineering, Data Science, Marketing")
    years_of_experience = models.PositiveIntegerField(default=0, blank=True, null=True)
    
    # --------------------------------
    # Skills & Goals (Crucial for GenAI Context)
    # --------------------------------
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated list of skills (e.g., Python, SQL, Project Management)")
    career_goals = models.TextField(blank=True, null=True, help_text="What is your ultimate career objective?")
    
    # --------------------------------
    # External Links
    # --------------------------------
    github_profile = models.URLField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    portfolio_website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Optional but recommended: Django Signals to auto-create a profile when a User is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()