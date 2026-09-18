from django import template

from bandhuapp.helpers import responsive_image

register = template.Library()


@register.simple_tag
def responsive_img(field):
    """Template-tag wrapper around `bandhuapp.helpers.responsive_image`.

    Returns `{src, srcset, width, height}` for a Django ImageField file, or
    `None` when a responsive rendition isn't available -- callers fall back
    to the field's plain `.url` exactly as before this tag existed.
    """
    return responsive_image(field)
