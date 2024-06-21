from django import template

register = template.Library()

@register.filter(name='range')
def range_filter(start, end):
    return range(start, end + 1)
