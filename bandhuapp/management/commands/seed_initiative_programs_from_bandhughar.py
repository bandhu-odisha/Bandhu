from django.core.management.base import BaseCommand

from applications.patriotism.models import (
    Activity as PatriotismActivity,
    ActivityCategory as PatriotismActivityCategory,
    Ashram as PatriotismAshram,
    Event as PatriotismEvent,
    HomeGalleryPhoto as PatriotismHomeGalleryPhoto,
    HomePage as PatriotismHomePage,
    Meeting as PatriotismMeeting,
    Photo as PatriotismPhoto,
    Attendee as PatriotismAttendee,
)
from applications.prasantaraktadan.models import (
    Activity as PrsActivity,
    ActivityCategory as PrsActivityCategory,
    Ashram as PrsAshram,
    Attendee as PrsAttendee,
    Event as PrsEvent,
    HomeGalleryPhoto as PrsHomeGalleryPhoto,
    HomePage as PrsHomePage,
    Meeting as PrsMeeting,
    Photo as PrsPhoto,
)
from applications.sevavrata.models import (
    Activity as SevavrataActivity,
    ActivityCategory as SevavrataActivityCategory,
    Ashram as SevavrataAshram,
    Attendee as SevavrataAttendee,
    Event as SevavrataEvent,
    HomeGalleryPhoto as SevavrataHomeGalleryPhoto,
    HomePage as SevavrataHomePage,
    Meeting as SevavrataMeeting,
    Photo as SevavrataPhoto,
)
from bandhuapp.initiative_program_seed import seed_initiative_homepage

PROGRAMS = (
    {
        'media_prefix': 'prasantaraktadan',
        'program_key': 'prasantaraktadan',
        'homepage_model': PrsHomePage,
        'ashram_model': PrsAshram,
        'activity_model': PrsActivity,
        'activity_category_model': PrsActivityCategory,
        'photo_model': PrsPhoto,
        'event_model': PrsEvent,
        'meeting_model': PrsMeeting,
        'attendee_model': PrsAttendee,
        'home_gallery_photo_model': PrsHomeGalleryPhoto,
    },
    {
        'media_prefix': 'patriotism',
        'program_key': 'patriotism',
        'homepage_model': PatriotismHomePage,
        'ashram_model': PatriotismAshram,
        'activity_model': PatriotismActivity,
        'activity_category_model': PatriotismActivityCategory,
        'photo_model': PatriotismPhoto,
        'event_model': PatriotismEvent,
        'meeting_model': PatriotismMeeting,
        'attendee_model': PatriotismAttendee,
        'home_gallery_photo_model': PatriotismHomeGalleryPhoto,
    },
    {
        'media_prefix': 'sevavrata',
        'program_key': 'sevavrata',
        'homepage_model': SevavrataHomePage,
        'ashram_model': SevavrataAshram,
        'activity_model': SevavrataActivity,
        'activity_category_model': SevavrataActivityCategory,
        'photo_model': SevavrataPhoto,
        'event_model': SevavrataEvent,
        'meeting_model': SevavrataMeeting,
        'attendee_model': SevavrataAttendee,
        'home_gallery_photo_model': SevavrataHomeGalleryPhoto,
    },
)


class Command(BaseCommand):
    help = 'Seed initiative program homepages (no Bandhughar import). Use --clear to remove imported year data.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all year entries, activities, gallery photos, and events before seeding homepage copy.',
        )

    def handle(self, *args, **options):
        clear_content = options['clear']
        for program in PROGRAMS:
            result = seed_initiative_homepage(
                clear_content=clear_content,
                stdout=self.stdout,
                **program,
            )
            self.stdout.write(self.style.SUCCESS(
                f"{result['program_label']}: homepage seeded, {result['program_count']} year entr(y/ies) in database."
            ))
