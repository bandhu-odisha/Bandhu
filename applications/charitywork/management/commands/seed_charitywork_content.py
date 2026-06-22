import os
import shutil
import urllib.error
import urllib.request
from datetime import date

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.charitywork.models import Charity, HomePage

TAGLINE = (
    'Patriotism In Action '
    '\u0b2a\u0b4d\u0b30\u0b5f\u0b4b\u0b17\u0b30\u0b47 \u0b26\u0b47\u0b36\u0b2a\u0b4d\u0b30\u0b47\u0b2e'
)

DESCRIPTION = (
    '<input type=button value="Registration Form" '
    'onclick="window.open(\'https://forms.gle/YrNJebMDWLFT5vah8\')" target="_blank" '
    'style="background-color:red;color:white"><br> '
    'Registration Start Date : 15 August 2023 <br> '
    'Registration Last Date : 15 September 2023 <br> '
    'Date of examination: 23 September 2023 <br> '
    'One day Personality Development camp and certificate distribution: 2 October 2023<br> '
    'You can contact us on Mob. No. 8249161884 in case of any query.'
)

HOMEPAGE_PICTURE = 'charity_work/index/Bandhu_Logo.jpeg'
HOMEPAGE_BANNER = 'charity_work/banner/our_mission.jpg'

CHARITIES = [
    {
        'slug': 'bandhu-academic-outreach-program-impart-knowledge',
        'title': 'Bandhu Academic Outreach Program',
        'purpose': 'Basic training on  Number Theory and Algebra',
        'location': 'Online Lectures',
        'description': (
            'Online Interactive Mathematics Training on NUMBER THEORY & ALGEBRA (OIMT-NA)'
        ),
        'image': 'charity_work/charities/Final_NT-Al-poster-page-001.jpg',
        'start_date': date(2020, 8, 17),
        'end_date': date(2020, 8, 21),
    },
    {
        'slug': 'bandhu-academic-outreach-program-road-beyond-comme',
        'title': 'Bandhu Academic Outreach Program',
        'purpose': 'Road Beyond Commerce',
        'location': 'Webinar',
        'description': 'Road Beyond Commerce',
        'image': 'charity_work/charities/Road_Beyond_Commerce-poster-page-001.jpg',
        'start_date': date(2020, 9, 12),
        'end_date': date(2020, 9, 12),
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
        for relative_path in {HOMEPAGE_PICTURE, HOMEPAGE_BANNER, *(row['image'] for row in CHARITIES)}:
            self._ensure_media_file(relative_path)

        homepage, _created = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                'tagline': TAGLINE,
                'description': DESCRIPTION,
                'picture': HOMEPAGE_PICTURE,
                'banner_image': HOMEPAGE_BANNER,
            },
        )
        homepage.tagline = TAGLINE
        homepage.description = DESCRIPTION
        homepage.picture = HOMEPAGE_PICTURE
        if not homepage.banner_image:
            homepage.banner_image = HOMEPAGE_BANNER
        homepage.save()

        keep_ids = []
        for row in CHARITIES:
            charity = Charity.objects.filter(slug=row['slug']).first()
            if not charity:
                charity = Charity.objects.filter(
                    title=row['title'],
                    location=row['location'],
                ).first()
            if not charity:
                charity = Charity()
            charity.title = row['title']
            charity.purpose = row['purpose']
            charity.location = row['location']
            charity.description = row['description']
            charity.image = row['image']
            charity.start_date = row['start_date']
            charity.end_date = row['end_date']
            charity.slug = row['slug']
            charity.save()
            keep_ids.append(charity.id)

        Charity.objects.exclude(id__in=keep_ids).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Seeded Other Activities homepage and {len(keep_ids)} activity card(s).'
        ))
