import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.charitywork.models import Charity, HomePage

TAGLINE = (
    'Patriotism In Action '
    '\u0b2a\u0b4d\u0b30\u0b5f\u0b4b\u0b17\u0b30\u0b47 \u0b26\u0b47\u0b36\u0b2a\u0b4d\u0b30\u0b47\u0b2e'
)

DESCRIPTION = (
    'Registration Start Date : 15 August 2023 Registration Last Date : 15 September 2023 '
    'Date of examination: 23 September 2023 One day Personality Development camp and '
    'certificate distribution: 2 October 2023 You can contact us on Mob. No. 8249161884 '
    'in case of any query.'
)

HOMEPAGE_PICTURE = 'charity_work/index/Bandhu_Logo.jpeg'
HOMEPAGE_BANNER = 'charity_work/banner/our_mission.jpg'

CHARITIES = [
    {
        'slug': 'bandhu-academic-outreach-program-road-beyond-commerce',
        'title': 'Bandhu Academic Outreach Program',
        'purpose': 'Road Beyond Commerce',
        'location': 'Webinar',
        'description': (
            'Road Beyond Commerce webinar as part of Bandhu Academic Outreach Program.'
        ),
        'image': 'charity_work/charities/Road_Beyond_Commerce-poster-page-001.jpg',
    },
    {
        'slug': 'bandhu-academic-outreach-program-number-theory-algebra',
        'title': 'Bandhu Academic Outreach Program',
        'purpose': 'Basic training on Number Theory and Algebra',
        'location': 'Online Lectures',
        'description': (
            'Basic training on Number Theory and Algebra through online lectures, '
            'part of Bandhu Academic Outreach Program.'
        ),
        'image': 'charity_work/charities/Final_NT-Al-poster-page-001.jpg',
    },
]


class Command(BaseCommand):
    help = 'Seed Other Activities homepage text and activity cards (aligned with live site).'

    def _ensure_media_file(self, relative_path):
        destination = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.isfile(destination):
            return True

        basename = os.path.basename(relative_path)
        source = os.path.join(settings.BASE_DIR, 'img', basename)
        if os.path.isfile(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True

        try:
            request = urllib.request.Request(
                f'https://bandhuodisha.in/media/{relative_path}',
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'https://bandhuodisha.in/other_activities/',
                },
            )
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(destination, 'wb') as output_file:
                    output_file.write(response.read())
            return True
        except (urllib.error.URLError, OSError):
            return False

    def handle(self, *args, **options):
        self._ensure_media_file(HOMEPAGE_PICTURE)
        self._ensure_media_file(HOMEPAGE_BANNER)
        for row in CHARITIES:
            self._ensure_media_file(row['image'])

        homepage = HomePage.objects.first()
        if not homepage:
            homepage = HomePage(
                tagline=TAGLINE,
                description=DESCRIPTION,
                picture=HOMEPAGE_PICTURE,
                banner_image=HOMEPAGE_BANNER,
            )
            homepage.save()
        else:
            homepage.tagline = TAGLINE
            homepage.description = DESCRIPTION
            if self._ensure_media_file(HOMEPAGE_PICTURE):
                homepage.picture = HOMEPAGE_PICTURE
            if self._ensure_media_file(HOMEPAGE_BANNER):
                homepage.banner_image = HOMEPAGE_BANNER
            homepage.save(update_fields=['tagline', 'description', 'picture', 'banner_image'])

        for row in CHARITIES:
            Charity.objects.update_or_create(
                slug=row['slug'],
                defaults={
                    'title': row['title'],
                    'purpose': row['purpose'],
                    'location': row['location'],
                    'description': row['description'],
                    'image': row['image'],
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded Other Activities homepage and {len(CHARITIES)} activity card(s).'
        ))
