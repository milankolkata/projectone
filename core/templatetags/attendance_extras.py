# attendance_extras.py inside the templatetags folder
from django import template
import calendar

register = template.Library()

@register.filter
def month_name(month_number):
    """Returns the month name given a month number."""
    return calendar.month_name[month_number]
