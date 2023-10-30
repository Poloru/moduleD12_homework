from django import template

register = template.Library()


@register.filter
def pow(value, pow):
    return value**pow


