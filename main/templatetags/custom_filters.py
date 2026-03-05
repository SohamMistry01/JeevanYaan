from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    
    # 1. Try accessing with the key exactly as passed (usually integer from the loop)
    value = dictionary.get(key)
    if value is not None:
        return value
        
    # 2. Fallback: Try accessing with the key as a string
    # (This fixes the issue where JSON session storage converts int keys to strings)
    return dictionary.get(str(key))