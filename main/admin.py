from django.contrib import admin
from .models import ModulesControl, UserModuleUsage, UserProfile

@admin.register(ModulesControl)
class ModulesControlAdmin(admin.ModelAdmin):
    list_display = ('name_of_module', 'role', 'daily_limit')
    list_filter = ('role', 'name_of_module')
    search_fields = ('name_of_module', 'role__name')

@admin.register(UserModuleUsage)
class UserModuleUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'module_name', 'date', 'usage_count')
    list_filter = ('date', 'module_name', 'user')
    search_fields = ('user__username', 'module_name')
    ordering = ('-date', '-usage_count')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_status', 'education_level', 'primary_domain')
    search_fields = ('user__username', 'user__email', 'primary_domain', 'skills')
    list_filter = ('current_status', 'education_level')
    
    # Group fields logically in the admin form
    fieldsets = (
        ('User Linking', {
            'fields': ('user',)
        }),
        ('Education & Status', {
            'fields': ('education_level', 'degree_name', 'current_status', 'primary_domain', 'years_of_experience')
        }),
        ('AI Context (Skills & Goals)', {
            'fields': ('skills', 'career_goals')
        }),
        ('Links', {
            'fields': ('github_profile', 'linkedin_profile', 'portfolio_website')
        }),
    )