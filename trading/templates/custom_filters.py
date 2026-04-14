# trading/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def abs(value):
    """Возвращает абсолютное значение"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
    
    
@register.filter
def dictsum(queryset, field):
    """Суммирует значения поля в queryset"""
    return sum(getattr(obj, field, 0) for obj in queryset)