from django import template
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def guest_avatar_url(guest):
    """Uploaded photo, else default man/woman illustration."""
    if guest.photo:
        return guest.photo.url
    gender = 'woman' if getattr(guest, 'avatar', 'man') == 'woman' else 'man'
    return static(f'img/{gender}.png')
