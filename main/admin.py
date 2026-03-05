from django.contrib import admin
from .models import ModulesControl, UserModuleUsage

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