from django import template

register = template.Library()

@register.filter
def is_admin(user):
    return (user.is_admin == True)