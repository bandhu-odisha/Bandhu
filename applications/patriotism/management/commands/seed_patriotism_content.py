from django.core.management.base import BaseCommand

from applications.patriotism.models import (
    Activity,
    ActivityCategory,
    Ashram,
    Attendee,
    Event,
    HomeGalleryPhoto,
    HomePage,
    Meeting,
    Photo,
)
from bandhuapp.initiative_program_seed import seed_initiative_homepage


class Command(BaseCommand):
    help = 'Seed Patriotism in Action homepage only (no Bandhughar import). Use --clear to wipe year data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all year entries and related content before seeding.',
        )

    def handle(self, *args, **options):
        result = seed_initiative_homepage(
            media_prefix='patriotism',
            program_key='patriotism',
            homepage_model=HomePage,
            clear_content=options['clear'],
            ashram_model=Ashram,
            activity_model=Activity,
            activity_category_model=ActivityCategory,
            photo_model=Photo,
            event_model=Event,
            meeting_model=Meeting,
            attendee_model=Attendee,
            home_gallery_photo_model=HomeGalleryPhoto,
            stdout=self.stdout,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {result['program_label']} homepage; "
            f"{result['program_count']} year entr(y/ies) in database."
        ))
