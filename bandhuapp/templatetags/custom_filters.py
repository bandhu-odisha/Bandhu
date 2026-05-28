import re

from django import template

from bandhuapp.helpers import proper_case

register = template.Library()


@register.filter
def proper_case_filter(value):
    return proper_case(value)


@register.filter
def proper_case_lines(value):
    """Apply proper_case to each line; preserves blank lines (paragraph breaks)."""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    lines = value.split("\n")
    return "\n".join(proper_case(line) if line.strip() else line for line in lines)


@register.filter
def single_line(value):
    """Collapse line breaks and repeated spaces so taglines stay on one line."""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    text = value.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip()


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
        return [proper_case(p.strip()) for p in parts if p.strip()]
    return [proper_case(profession)]
