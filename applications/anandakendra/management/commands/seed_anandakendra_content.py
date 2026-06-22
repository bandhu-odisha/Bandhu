import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.anandakendra.models import AnandaKendra, HomePage, Photo

ANANDAKENDRA_INTRO = (
    '<strong>The Idea and the objective:</strong> Bandhu Anandakendra, henceforward called Kendra, '
    'is conceived to support the school education in all possible ways. It is observed '
    'that there are children in villages, whose parents cannot or are not willing to afford '
    'to care for their education. These children need to be assisted for completing the school '
    'education successfully. Successfully, not only in terms of good marks in the examinations '
    'but also in terms of a sound understanding of fundamentals. More importantly, this initiative '
    'aims to ensure a supportive environment for an overall (personal-social-spiritual) development '
    'at a tender stage of life. We can hope them to be the torch bearers of the idea Bandhu stands '
    'for, with a keen fellow-feeling, a broader and deeper outlook towards life and with a sincere urge '
    'to serve. They are supposed to be prepared to accept, face and lead a life overcoming all its '
    'challenges, trials and tribulations and to materialise all the possibilities to excel. It is not '
    'meant to be the replacement of a school but to take care of the children beyond school hours. '
    'We hope this shall check dropouts from schools and ensure social equality in localities served '
    'by the Anandakendras. In the process, some identified poor but meritorious students shall be '
    'helped in their pursuits of education. This includes helping them in qualifying Olympiad '
    'examinations and Nabodaya Vidyalaya Samiti examinations and anything required for their '
    'academic progress.  '
    '\r\n<br><br>\r\n'
    '<strong> Modus Operandi:</strong> Weekly sessions on Sunday mornings are meant for '
    'developing spiritual, physical and emotional culture among children. This includes yogabhyas, '
    'creative and delightful games, inspiring songs, storytelling and other creative activities.  '
    'Daily guidance for 2 hours on school curriculum is provided beyond school timing. A Kendra is '
    'supposed to be run by one or two youth, who have preferably completed or are continuing '
    'their college education. They are called Anandakendra Acharyas/Acharyaas. A token amount '
    'is to be given to them for their invaluable service to their brothers and sisters. Bandhu is to '
    'assist in their academic pursuits in some possible ways. Training and review at regular intervals '
    'are to be conducted to ensure smooth functioning and continuous improvement of Kendras.'
)

RUNNING_KENDRAS = [
    {
        'name': 'Anandakendra',
        'locality': 'Bandhu Ashram, Odisha',
        'description': 'Bandhu Ashram, Odisha',
        'image': 'anandkendra/kendras/pimg3.jpg',
        'slug': 'anandakendra-1-jabalpur',
    },
    {
        'name': 'AnandaKendra 2',
        'locality': 'Odisha',
        'description': 'Odisha',
        'image': 'anandkendra/kendras/clients-bg1.jpg',
        'slug': 'anandakendra-2-odisha',
    },
    {
        'name': 'Anandakendra',
        'locality': 'Odisha',
        'description': 'Odisha',
        'image': 'anandkendra/kendras/photo.jpg',
        'slug': 'anandakendra-odisha',
    },
]

# Per-kendra gallery images on production (stored under anandkendra/activities/).
KENDRA_GALLERY_IMAGES = {
    'anandakendra-1-jabalpur': [
        'anandkendra/activities/pimg9.jpg',
        'anandkendra/activities/pimg8.jpg',
        'anandkendra/activities/pimg7.jpg',
        'anandkendra/activities/pimg6.jpg',
        'anandkendra/activities/pimg5.jpg',
        'anandkendra/activities/pimg4.jpg',
    ],
    'anandakendra-2-odisha': [
        'anandkendra/activities/Screenshot_157.png',
    ],
}


class Command(BaseCommand):
    help = 'Seed Anandakendra homepage intro and running kendra cards from live content.'

    def _ensure_media_file(self, relative_path, referer='https://bandhuodisha.in/anandakendra/'):
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
                headers={'User-Agent': 'Mozilla/5.0', 'Referer': referer},
            )
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(destination, 'wb') as output_file:
                    output_file.write(response.read())
            return True
        except (urllib.error.URLError, OSError):
            return False

    def _sync_kendra_gallery(self, kendra, image_paths):
        keep_ids = []
        for relative_path in image_paths:
            if not self._ensure_media_file(relative_path):
                self.stdout.write(self.style.WARNING(f'Missing gallery file: {relative_path}'))
                continue

            photo = Photo.objects.filter(kendra=kendra, picture=relative_path).first()
            if not photo:
                photo = Photo(kendra=kendra)
            photo.picture.name = relative_path
            photo.approved = True
            photo.save()
            keep_ids.append(photo.id)

        Photo.objects.filter(kendra=kendra).exclude(id__in=keep_ids).delete()
        return len(keep_ids)

    def handle(self, *args, **options):
        picture_path = 'anandakendra/index/clients-bg1.jpg'
        banner_path = 'anandakendra/banner/our_mission.jpg'
        for relative_path in (picture_path, banner_path):
            picture_abs = os.path.join(settings.MEDIA_ROOT, relative_path)
            if not os.path.isfile(picture_abs):
                source_abs = os.path.join(settings.BASE_DIR, 'img', os.path.basename(relative_path))
                if os.path.isfile(source_abs):
                    os.makedirs(os.path.dirname(picture_abs), exist_ok=True)
                    shutil.copy2(source_abs, picture_abs)

        homepage, _created = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                'tagline': '',
                'description': ANANDAKENDRA_INTRO,
                'picture': picture_path,
                'banner_image': banner_path,
            },
        )
        homepage.tagline = ''
        homepage.description = ANANDAKENDRA_INTRO
        homepage.picture = picture_path
        if not homepage.banner_image:
            homepage.banner_image = banner_path
        homepage.save()

        keep_ids = []
        for row in RUNNING_KENDRAS:
            image_path = row['image']
            image_abs = os.path.join(settings.MEDIA_ROOT, image_path)
            if not os.path.isfile(image_abs):
                source_abs = os.path.join(settings.BASE_DIR, 'img', os.path.basename(image_path))
                if os.path.isfile(source_abs):
                    os.makedirs(os.path.dirname(image_abs), exist_ok=True)
                    shutil.copy2(source_abs, image_abs)
                else:
                    try:
                        req = urllib.request.Request(
                            f"https://bandhuodisha.in/media/{image_path}",
                            headers={
                                "User-Agent": "Mozilla/5.0",
                                "Referer": "https://bandhuodisha.in/anandakendra/",
                            },
                        )
                        os.makedirs(os.path.dirname(image_abs), exist_ok=True)
                        with urllib.request.urlopen(req, timeout=30) as response:
                            with open(image_abs, "wb") as handle:
                                handle.write(response.read())
                    except (urllib.error.URLError, OSError):
                        pass

            kendra, _created = AnandaKendra.objects.get_or_create(
                name=row['name'],
                locality=row['locality'],
                defaults={
                    'description': row['description'],
                    'address': row['locality'],
                    'image': image_path,
                    'slug': row['slug'],
                },
            )
            kendra.description = row['description']
            if not (kendra.address or '').strip():
                kendra.address = row['locality']
            kendra.slug = row['slug']
            kendra.image = image_path
            keep_ids.append(kendra.id)
            kendra.save()

        AnandaKendra.objects.exclude(id__in=keep_ids).delete()

        gallery_total = 0
        for kendra in AnandaKendra.objects.filter(slug__in=KENDRA_GALLERY_IMAGES):
            gallery_total += self._sync_kendra_gallery(
                kendra,
                KENDRA_GALLERY_IMAGES[kendra.slug],
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded Anandakendra home content, {len(keep_ids)} running kendras, '
            f'and {gallery_total} gallery photo(s).'
        ))
