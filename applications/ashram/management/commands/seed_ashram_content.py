import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.ashram.models import Activity, ActivityCategory, Ashram, HomePage, Photo

BANDHUGHAR_INTRO = 'Come, See, Feel and Enjoy the Goodness.....'

RUNNING_BANDHUGHARS = [
    {
        'name': 'Amrut Mahotsav celebration',
        'locality': 'Lankapara',
        'description': 'Activities at Bandhu Ashram',
        'address': 'Lankapara, Odisha',
        'image': 'ashram/thumbnails/22.jpg',
        'slug': 'Activities_Bandhu_Ashram',
    },
    {
        'name': 'Visit by school kids',
        'locality': 'Lankapara',
        'description': 'Visit by school kids',
        'address': 'Lankapara, Odisha',
        'image': 'ashram/thumbnails/collage.jpg',
        'slug': 'bandhu-ghar-celebration-lankapara',
    },
]

BANDHUGHAR_GALLERY_IMAGES = {
    'Activities_Bandhu_Ashram': ['ashram/2.jpg'],
}

BANDHUGHAR_ACTIVITIES = {
    'Activities_Bandhu_Ashram': [
        {
            'category': 'Amrut Mahotsav celebration',
            'name': 'Amrut Mahotsav celebration',
            'description': 'amrut mahotsav celebration',
        },
    ],
}


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

    def _sync_activities(self, ashram, activity_rows):
        keep_activity_ids = []
        keep_category_ids = []

        for row in activity_rows:
            category, _created = ActivityCategory.objects.get_or_create(
                ashram=ashram,
                name=row['category'],
            )
            keep_category_ids.append(category.id)

            activity = Activity.objects.filter(
                category=category,
                name=row['name'],
            ).first()
            if not activity:
                activity = Activity(category=category)
            activity.name = row['name']
            activity.description = row['description']
            activity.save()
            keep_activity_ids.append(activity.id)

        Activity.objects.filter(category__ashram=ashram).exclude(
            id__in=keep_activity_ids,
        ).delete()
        ActivityCategory.objects.filter(ashram=ashram).exclude(
            id__in=keep_category_ids,
        ).delete()
        return len(keep_activity_ids)

    def handle(self, *args, **options):
        picture_path = 'ashram/index/21.jpg'
        self._ensure_media_image(picture_path)

        homepage, _created = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                'tagline': 'An Abode for Goodness',
                'description': BANDHUGHAR_INTRO,
                'picture': picture_path,
            },
        )
        homepage.tagline = 'An Abode for Goodness'
        homepage.description = BANDHUGHAR_INTRO
        homepage.picture = picture_path
        from bandhuapp.initiative_home_captions import apply_initiative_captions
        apply_initiative_captions(homepage, 'ashram')
        homepage.save()

        keep_ids = []
        for row in RUNNING_BANDHUGHARS:
            self._ensure_media_image(row['image'])
            bandhughar = Ashram.objects.filter(
                name=row['name'],
                locality=row['locality'],
            ).first()
            if not bandhughar:
                bandhughar = Ashram.objects.filter(slug=row['slug']).first()
            if not bandhughar:
                bandhughar = Ashram()
            bandhughar.name = row['name']
            bandhughar.locality = row['locality']
            bandhughar.description = row['description']
            bandhughar.address = row['address']
            bandhughar.image = row['image']
            bandhughar.slug = row['slug']
            bandhughar.save()
            keep_ids.append(bandhughar.id)

        Ashram.objects.exclude(id__in=keep_ids).delete()

        gallery_total = 0
        for ashram in Ashram.objects.filter(slug__in=BANDHUGHAR_GALLERY_IMAGES):
            keep_photo_ids = []
            for relative_path in BANDHUGHAR_GALLERY_IMAGES[ashram.slug]:
                if not self._ensure_media_image(relative_path):
                    self.stdout.write(self.style.WARNING(f'Missing gallery file: {relative_path}'))
                    continue
                photo = Photo.objects.filter(ashram=ashram, picture=relative_path).first()
                if not photo:
                    photo = Photo(ashram=ashram)
                photo.picture.name = relative_path
                photo.approved = True
                photo.save()
                keep_photo_ids.append(photo.id)
            Photo.objects.filter(ashram=ashram).exclude(id__in=keep_photo_ids).delete()
            gallery_total += len(keep_photo_ids)

        activity_total = 0
        for ashram in Ashram.objects.filter(slug__in=BANDHUGHAR_ACTIVITIES):
            activity_total += self._sync_activities(
                ashram,
                BANDHUGHAR_ACTIVITIES[ashram.slug],
            )
        for ashram in Ashram.objects.exclude(slug__in=BANDHUGHAR_ACTIVITIES):
            Activity.objects.filter(category__ashram=ashram).delete()
            ActivityCategory.objects.filter(ashram=ashram).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Seeded Bandhughar home content, {len(keep_ids)} Bandhughars, '
            f'{gallery_total} gallery photo(s), and {activity_total} activit(ies).'
        ))
