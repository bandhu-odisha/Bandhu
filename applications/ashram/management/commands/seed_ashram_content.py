import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.ashram.models import Ashram, HomePage


BANDHUGHAR_INTRO = 'Come, See, Feel and Enjoy the Goodness.....'

RUNNING_BANDHUGHARS = [
    {
        'name': 'Amrut Mahotsav celebration',
        'locality': 'Lankapara',
        'description': 'Amrut Mahotsav celebration at Bandhughar, Lankapara.',
        'address': 'Bandhughar, Lankapara, Odisha',
        'image': 'ashram/thumbnails/22.jpg',
        'slug': 'amrut-mahotsav-celebration-lankapara',
    },
    {
        'name': 'Visit by school kids',
        'locality': 'Lankapara',
        'description': 'Visit by school kids to Bandhughar, Lankapara.',
        'address': 'Bandhughar, Lankapara, Odisha',
        'image': 'ashram/thumbnails/collage.jpg',
        'slug': 'visit-by-school-kids-lankapara',
    },
]


class Command(BaseCommand):
    help = 'Seed Bandhughar homepage intro and Bandhughar cards from live content.'

    def _ensure_media_image(self, relative_path):
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
                    'Referer': 'https://bandhuodisha.in/bandhughar/',
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
        homepage = HomePage.objects.first()
        if homepage:
            banner_image = 'ashram/index/21.jpg'
            self._ensure_media_image(banner_image)
            homepage.tagline = 'An Abode for Goodness'
            homepage.description = BANDHUGHAR_INTRO
            homepage.picture = banner_image
            homepage.save(update_fields=['tagline', 'description', 'picture'])

        keep_ids = []
        for row in RUNNING_BANDHUGHARS:
            self._ensure_media_image(row['image'])
            bandhughar, _created = Ashram.objects.get_or_create(
                slug=row['slug'],
                defaults={
                    'name': row['name'],
                    'locality': row['locality'],
                    'description': row['description'],
                    'address': row['address'],
                    'image': row['image'],
                },
            )
            bandhughar.name = row['name']
            bandhughar.locality = row['locality']
            bandhughar.description = row['description']
            bandhughar.address = row['address']
            bandhughar.image = row['image']
            bandhughar.save()
            keep_ids.append(bandhughar.id)

        Ashram.objects.exclude(id__in=keep_ids).delete()
        self.stdout.write(self.style.SUCCESS(f'Seeded Bandhughar home content and {len(keep_ids)} Bandhughars.'))
