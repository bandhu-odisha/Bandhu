from django import template

register = template.Library()


@register.filter
def to_snake_case(value):
    return value.replace(" ", "-").lower()


@register.filter
def null_to_hyphen(value):
    if not value:
        return "-"
    return value
