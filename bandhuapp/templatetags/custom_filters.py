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


@register.filter
def profession_lines(profession, designation_title):
    """For Office Bearers, split 'position, occupation' into separate lines; else return single line.
    Uses last ', ' so positions that contain commas (e.g. 'Joint Secretary (Social media, Outreach and Website)') parse correctly."""
    if not profession:
        return [""]
    title = (designation_title or "").strip()
    if title in ("Office Bearers", "Other") and ", " in profession:
        parts = profession.rsplit(", ", 1)
        return [p.strip() for p in parts if p.strip()]
    return [profession]
