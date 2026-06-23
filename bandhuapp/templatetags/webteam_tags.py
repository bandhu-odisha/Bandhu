from django import template

from bandhuapp.webteam import webteam_footer_context

register = template.Library()


@register.inclusion_tag('snippets/webteam_credits.html')
def webteam_credits():
    return webteam_footer_context()
