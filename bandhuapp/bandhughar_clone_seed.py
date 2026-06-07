"""Deprecated: Bandhughar import removed. Use bandhuapp.initiative_program_seed instead."""

from bandhuapp.initiative_program_seed import clear_program_content, seed_initiative_homepage

__all__ = ['clear_program_content', 'seed_initiative_homepage', 'seed_bandhughar_clone']


def seed_bandhughar_clone(*, media_prefix, program_label, download_referer, homepage_model, **kwargs):
    """Backward-compatible entry point; seeds homepage only and does not import Bandhughar data."""
    program_key = media_prefix
    if program_key not in ('prasantaraktadan', 'patriotism', 'sevavrata'):
        raise ValueError(f'Unknown initiative program: {program_key}')

    ashram_model = kwargs.get('ashram_model')
    result = seed_initiative_homepage(
        media_prefix=media_prefix,
        program_key=program_key,
        homepage_model=homepage_model,
        clear_content=False,
        ashram_model=ashram_model,
        activity_model=kwargs.get('activity_model'),
        activity_category_model=kwargs.get('activity_category_model'),
        photo_model=kwargs.get('photo_model'),
        event_model=kwargs.get('event_model'),
        meeting_model=kwargs.get('meeting_model'),
        attendee_model=kwargs.get('attendee_model'),
        home_gallery_photo_model=kwargs.get('home_gallery_photo_model'),
        stdout=kwargs.get('stdout'),
    )
    return {
        'program_count': result['program_count'],
        'gallery_total': 0,
        'activity_total': 0,
        'program_label': program_label or result['program_label'],
    }
