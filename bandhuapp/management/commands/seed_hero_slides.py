"""
Seed HeroSlide records from the content previously hardcoded in Hero.jsx.
Idempotent — safe to run multiple times.

Usage: python manage.py seed_hero_slides
"""
import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from bandhuapp.models import HeroSlide

SLIDES = [
    {
        'order': 0,
        'title': 'An idea - ଏକ ବିଚାର',
        'subtitle': 'Bandhu is an idea that celebrates goodness — in you, me, and all others.',
        'src_static': 'our_mission.jpg',
    },
    {
        'order': 1,
        'title': 'Good but not necessarily Great',
        'subtitle': (
            'We are concerned about the inconsistencies within and without — '
            'and choose to do small things with the highest possible sincerity.'
        ),
        'src_static': 'our_mission1.jpg',
    },
    {
        'order': 2,
        'title': 'Bandhu at twilight - ବନ୍ଧୁଘର',
        'subtitle': 'An abode for goodness with boundless vibes of friendship.',
        'src_static': 'about-slide-3-campus.png',
    },
    {
        'order': 3,
        'title': 'Blossoming in Silence - ନୀରବରେ ଫୁଟୁଥିବା ଫୁଲଟିଏ',
        'subtitle': 'Like the garden we tend, our work grows with patience, colour, and hope — in Odisha and beyond.',
        'src_static': 'about-slide-2-hibiscus.png',
    },
]

DEST_DIR = os.path.join(settings.MEDIA_ROOT, 'bandhuapp', 'hero')


def _resolve_src(filename):
    """Find image in static/img/ or img/ fallback dirs."""
    for base in (
        os.path.join(settings.BASE_DIR, 'static', 'img'),
        os.path.join(settings.BASE_DIR, 'img'),
    ):
        path = os.path.join(base, filename)
        if os.path.isfile(path):
            return path
    return None


class Command(BaseCommand):
    help = 'Seed Hero slides from previously hardcoded Hero.jsx content (idempotent).'

    def handle(self, *args, **options):
        os.makedirs(DEST_DIR, exist_ok=True)
        created = skipped = 0

        for slide in SLIDES:
            src_path = _resolve_src(slide['src_static'])
            if src_path:
                dest_filename = f"hero_{slide['order']}_{slide['src_static']}"
                dest_path = os.path.join(DEST_DIR, dest_filename)
                if not os.path.exists(dest_path):
                    shutil.copy2(src_path, dest_path)
                image_field_value = f"bandhuapp/hero/{dest_filename}"
            else:
                self.stderr.write(f"  ⚠  Source image not found: {slide['src_static']} — slide will have no image")
                image_field_value = ''

            obj, was_created = HeroSlide.objects.get_or_create(
                order=slide['order'],
                defaults={
                    'title': slide['title'],
                    'subtitle': slide['subtitle'],
                    'image': image_field_value,
                    'is_active': True,
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'seed_hero_slides: {created} created, {skipped} already existed.'
            )
        )
