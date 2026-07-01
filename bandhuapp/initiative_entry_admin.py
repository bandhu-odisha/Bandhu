"""Shared admin fieldsets for initiative entry models (centers, years, activities)."""

from bandhuapp.initiative_home_admin import INITIATIVE_HERO_HELP

ENTRY_HERO_FIELDSET = (
    'Hero image & caption',
    {
        'fields': ('image_caption_en', 'image_caption_or'),
        'description': INITIATIVE_HERO_HELP,
    },
)


def entry_hero_fieldset(image_field):
    """Hero image field name varies per model (`image`, `logo`, etc.)."""
    return (
        'Hero image & caption',
        {
            'fields': (image_field, 'image_caption_en', 'image_caption_or'),
            'description': INITIATIVE_HERO_HELP,
        },
    )
