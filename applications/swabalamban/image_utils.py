from django.templatetags.static import static


def image_field_url(image_field):
    """Return the media URL only when the file exists in storage."""
    if not image_field or not image_field.name:
        return None
    try:
        if image_field.storage.exists(image_field.name):
            return image_field.url
    except Exception:
        return None
    return None


def static_image_url(relative_path):
    return static(relative_path)
