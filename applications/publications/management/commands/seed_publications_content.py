import os
import shutil
import urllib.error
import urllib.request
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from applications.publications.models import HomePage, Publication

CARD_PICTURE = 'publications/index/our_mission.jpg'

# Aligned with https://bandhuodisha.in/publications/ (titles, slugs, media paths, dates).
PUBLICATIONS = [
    {
        'slug': 'annual-report-24-2025',
        'title': 'Annual Report 24-2025',
        'description': 'Bandhu annual report for the year 2024–25.',
        'thumb': 'publications/thumb/ar2425.JPG',
        'media': 'publications/Bandhu_fLrWRJJ.pdf',
        'created': datetime(2025, 11, 6, 12, 0, 0),
    },
    {
        'slug': 'Ankurayan-report-2024',
        'title': 'Ankurayan report 2024',
        'description': 'Report in brief — Ankurayan 2024.',
        'thumb': 'publications/thumb/Ankurayan2024.jpeg',
        'media': 'publications/Report_in_brief-Ankurayan2024.pdf',
        'created': datetime(2025, 10, 22, 12, 0, 0),
    },
    {
        'slug': 'paika-2019',
        'title': 'Paika 2019',
        'description': 'Paika 2019 — Bandhu community mouthpiece.',
        'thumb': 'publications/thumb/paika2019_VhEXvVo.png',
        'media': 'publications/PAIKA_2019-compressed.pdf',
        'created': datetime(2024, 10, 24, 12, 0, 0),
    },
    {
        'slug': 'glance-bandhu',
        'title': 'A glance of Bandhu',
        'description': 'A short introduction to Bandhu and its work.',
        'thumb': 'publications/thumb/bandhu_logo.jpg',
        'media': 'publications/Bandhu-a-glance.pdf',
        'created': datetime(2020, 9, 13, 12, 0, 0),
    },
    {
        'slug': 'sample-copy-invitation-card-ankurayan',
        'title': 'Sample copy of an invitation card of Ankurayan',
        'description': 'Sample invitation artwork for Ankurayan.',
        'thumb': 'publications/thumb/athara_ra_nimantrana.jpg',
        'media': 'publications/athara_ra_nimantrana.jpg',
        'created': datetime(2020, 9, 2, 12, 0, 0),
    },
    {
        'slug': 'bandhu-ek-bichar',
        'title': 'Bandhu Ek Bichar',
        'description': 'Bandhu Ek Bichar publication.',
        'thumb': 'publications/thumb/Bandhu-eka_bichara.jpg',
        'media': 'publications/Bandhu-eka_bichara.jpg',
        'created': datetime(2020, 9, 2, 12, 0, 0),
    },
    {
        'slug': 'paika-2016',
        'title': 'Paika 2016',
        'description': 'Paika 2016 issue.',
        'thumb': 'publications/thumb/paika2016.jpeg',
        'media': 'publications/paika2016_LcVmKsJ.jpeg',
        'created': datetime(2020, 9, 1, 12, 0, 0),
    },
    {
        'slug': 'paika-2015',
        'title': 'Paika 2015',
        'description': 'Paika 2015 issue.',
        'thumb': 'publications/thumb/Paika2015_GLepb7k.jpeg',
        # Live list uses this file under publications/ (not thumb/); save into thumb/ for the model.
        'thumb_download_from': 'publications/Paika2015_GLepb7k.jpeg',
        'media': 'publications/Paika2015_6YfzM4Z.jpeg',
        'created': datetime(2020, 9, 1, 12, 0, 0),
    },
    {
        'slug': 'paika-2014',
        'title': 'Paika 2014',
        'description': 'Paika 2014 issue.',
        'thumb': 'publications/thumb/Paika-2014.jpeg',
        'media': 'publications/Paika-2014_nMoHoDX.jpeg',
        'created': datetime(2020, 9, 1, 12, 0, 0),
    },
    {
        'slug': 'kalam-2011-and-kalam-2012',
        'title': 'Kalam 2011',
        'description': 'Kalam 2011 publication.',
        'thumb': 'publications/thumb/kalam2011.png',
        'media': 'publications/kalama2011.pdf',
        'created': datetime(2020, 9, 1, 12, 0, 0),
    },
]


class Command(BaseCommand):
    help = 'Seed Publications homepage banner and publication rows; sync files to MEDIA_ROOT.'

    def _ensure_file(self, relative_path, download_from=None):
        destination = os.path.join(settings.MEDIA_ROOT, relative_path)
        if os.path.isfile(destination):
            return True

        basename = os.path.basename(relative_path)
        source = os.path.join(settings.BASE_DIR, 'img', basename)
        if os.path.isfile(source):
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
            return True

        live_path = download_from or relative_path
        try:
            request = urllib.request.Request(
                f'https://bandhuodisha.in/media/{live_path}',
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'https://bandhuodisha.in/publications/',
                },
            )
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with urllib.request.urlopen(request, timeout=45) as response:
                with open(destination, 'wb') as output_file:
                    output_file.write(response.read())
            return True
        except (urllib.error.URLError, OSError):
            return False

    def handle(self, *args, **options):
        self._ensure_file(CARD_PICTURE)

        homepage = HomePage.objects.first()
        if not homepage:
            homepage = HomePage(picture=CARD_PICTURE)
            homepage.save()
        else:
            if self._ensure_file(CARD_PICTURE) and not homepage.picture:
                homepage.picture = CARD_PICTURE
                homepage.save(update_fields=['picture'])

        keep_slugs = {row['slug'] for row in PUBLICATIONS}
        Publication.objects.exclude(slug__in=keep_slugs).delete()

        for row in PUBLICATIONS:
            self._ensure_file(
                row['thumb'],
                download_from=row.get('thumb_download_from'),
            )
            self._ensure_file(row['media'])

            created = timezone.make_aware(row['created'], timezone.get_current_timezone())
            Publication.objects.update_or_create(
                slug=row['slug'],
                defaults={
                    'title': row['title'],
                    'description': row['description'],
                    'thumb': row['thumb'],
                    'media': row['media'],
                    'by': None,
                    'is_visible': True,
                    'created': created,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded publications banner and {len(PUBLICATIONS)} publication(s).'
        ))
