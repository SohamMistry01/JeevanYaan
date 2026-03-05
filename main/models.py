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