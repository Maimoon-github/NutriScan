from django import template

register = template.Library()


@register.filter
def replace(value, arg):
    """Replace all occurrences of arg with a space"""
    if not value:
        return value
    parts = arg.split(',')
    if len(parts) == 2:
        old = parts[0].strip()
        new = parts[1].strip()
        return str(value).replace(old, new)
    return value


@register.filter
def replace_underscore(value):
    """Replace underscores with spaces and title case"""
    if not value:
        return value
    return str(value).replace('_', ' ').title()
