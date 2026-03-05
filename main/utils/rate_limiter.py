from django.contrib.auth.models import Group
from django.utils import timezone
from main.models import ModulesControl, UserModuleUsage 

def check_and_get_limit(user, module_name):
    """
    Evaluates if a user can use a module.
    Returns a tuple: (Boolean allowed, Object/String context)
    """
    if not user.is_authenticated:
        return False, "You must be logged in to use this tool."

    # 1. Identify User Role (Group)
    user_groups = user.groups.all()
    if not user_groups.exists():
        # Fallback to 'External Users' role if no group is assigned
        default_group, created = Group.objects.get_or_create(name='External Users')
        user.groups.add(default_group)
        user_groups = [default_group]

    # 2. Check if there are any limits defined for this module and the user's roles
    limits = ModulesControl.objects.filter(name_of_module=module_name, role__in=user_groups)
    
    if not limits.exists():
        # No limitation is defined in the table for this module/role -> Unlimited
        return True, None
        
    # If a user belongs to multiple groups, grant them the highest limit available
    max_daily_limit = max([limit.daily_limit for limit in limits])

    # 3. Get today's usage for this user and module
    today = timezone.now().date()
    usage_record, created = UserModuleUsage.objects.get_or_create(
        user=user,
        module_name=module_name,
        date=today
    )

    # 4. Evaluate limit
    if usage_record.usage_count >= max_daily_limit:
        return False, f"Daily Quota Exceeded: You have reached your limit of {max_daily_limit} uses for this tool today. Please try again tomorrow."

    # Return True and the usage record so we can increment it later
    return True, usage_record