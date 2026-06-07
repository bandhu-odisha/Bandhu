"""Seed initiative program homepages without importing Bandhughar year data."""

import os
import shutil

from django.conf import settings

INITIATIVE_HOME_COPY = {
    'prasantaraktadan': {
        'program_label': 'Prasanta Raktadan Shibir',
        'tagline': 'Prasanta Raktadan Shibir',
        'description': (
            'Voluntary blood donation camps across Odisha, bringing communities together '
            'to save lives through regular donation drives.'
        ),
    },
    'patriotism': {
        'program_label': 'Patriotism in Action',
        'tagline': 'Patriotism in Action',
        'description': (
            'Programs that nurture love for the nation through service, remembrance, '
            'and community participation.'
        ),
    },
    'sevavrata': {
        'program_label': 'Odisha Satabdi Sevavrata',
        'tagline': 'Odisha Satabdi Sevavrata',
        'description': (
            'Volunteer service initiatives marking Odisha’s centenary through meaningful '
            'community seva and outreach.'
        ),
    },
}

_FALLBACK_IMAGE_NAMES = ('our_mission1.jpg', 'pimg3.jpg', 'our_mission.jpg')


def _media_path(relative_path):
    return os.path.join(settings.MEDIA_ROOT, relative_path)


def _copy_fallback_image(relative_path):
    """Place a generic static image at relative_path (no Bandhughar media)."""
    destination = _media_path(relative_path)
    if os.path.isfile(destination):
        return True

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    for name in _FALLBACK_IMAGE_NAMES:
        for root in (
            os.path.join(settings.BASE_DIR, 'static', 'img'),
            os.path.join(settings.BASE_DIR, 'img'),
        ):
            source = os.path.join(root, name)
            if os.path.isfile(source):
                shutil.copy2(source, destination)
                return True
    return False


def clear_program_content(
    *,
    ashram_model,
    activity_model,
    activity_category_model,
    photo_model,
    event_model=None,
    meeting_model=None,
    attendee_model=None,
    home_gallery_photo_model=None,
):
    """Remove all year entries and related content; keep homepage row."""
    if attendee_model is not None:
        attendee_model.objects.all().delete()
    if meeting_model is not None:
        meeting_model.objects.all().delete()
    if event_model is not None:
        event_model.objects.all().delete()
    photo_model.objects.all().delete()
    activity_model.objects.all().delete()
    activity_category_model.objects.all().delete()
    ashram_model.objects.all().delete()
    if home_gallery_photo_model is not None:
        home_gallery_photo_model.objects.all().delete()


def seed_initiative_homepage(
    *,
    media_prefix,
    program_key,
    homepage_model,
    clear_content=False,
    ashram_model=None,
    activity_model=None,
    activity_category_model=None,
    photo_model=None,
    event_model=None,
    meeting_model=None,
    attendee_model=None,
    home_gallery_photo_model=None,
    stdout=None,
):
    """Seed program homepage copy only. Optionally clear imported year data first."""
    copy = INITIATIVE_HOME_COPY[program_key]
    if clear_content and all(
        model is not None
        for model in (
            ashram_model,
            activity_model,
            activity_category_model,
            photo_model,
        )
    ):
        clear_program_content(
            ashram_model=ashram_model,
            activity_model=activity_model,
            activity_category_model=activity_category_model,
            photo_model=photo_model,
            event_model=event_model,
            meeting_model=meeting_model,
            attendee_model=attendee_model,
            home_gallery_photo_model=home_gallery_photo_model,
        )
        if stdout:
            stdout.write(f"Cleared imported content for {copy['program_label']}.")

    picture_path = f'{media_prefix}/index/home.jpg'
    banner_path = f'{media_prefix}/banner/home.jpg'
    for relative_path in (picture_path, banner_path):
        if not _copy_fallback_image(relative_path) and stdout:
            stdout.write(f'Warning: no fallback image for {relative_path}')

    homepage, _created = homepage_model.objects.get_or_create(
        pk=1,
        defaults={
            'tagline': copy['tagline'],
            'description': copy['description'],
            'picture': picture_path,
            'banner_image': banner_path,
        },
    )
    homepage.tagline = copy['tagline']
    homepage.description = copy['description']
    if os.path.isfile(_media_path(picture_path)):
        homepage.picture = picture_path
    if os.path.isfile(_media_path(banner_path)):
        homepage.banner_image = banner_path
    homepage.save()

    return {
        'program_label': copy['program_label'],
        'program_count': ashram_model.objects.count() if ashram_model is not None else 0,
    }
