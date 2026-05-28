import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.anandakendra.models import AnandaKendra, HomePage

ANANDAKENDRA_INTRO = (
    'The Idea and the objective: Bandhu Anandakendra, henceforward called Kendra, '
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
    'academic progress. Modus Operandi: Weekly sessions on Sunday mornings are meant for '
    'developing spiritual, physical and emotional culture among children. This includes yogabhyas, '
    'creative and delightful games, inspiring songs, storytelling and other creative activities. Daily '
    'guidance for 2 hours on school curriculum is provided beyond school timing. A Kendra is '
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


class Command(BaseCommand):
    help = 'Seed Anandakendra homepage intro and running kendra cards from live content.'

    def handle(self, *args, **options):
        homepage = HomePage.objects.first()
        if homepage:
            picture_path = 'anandkendra/kendras/clients-bg1.jpg'
            picture_abs = os.path.join(settings.MEDIA_ROOT, picture_path)
            if not os.path.isfile(picture_abs):
                source_abs = os.path.join(settings.BASE_DIR, 'img', 'clients-bg1.jpg')
                if os.path.isfile(source_abs):
                    os.makedirs(os.path.dirname(picture_abs), exist_ok=True)
                    shutil.copy2(source_abs, picture_abs)
            homepage.tagline = 'The overall development of Kids...'
            homepage.description = ANANDAKENDRA_INTRO
            homepage.picture = picture_path
            homepage.save(update_fields=['tagline', 'description', 'picture'])

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
        self.stdout.write(self.style.SUCCESS(f'Seeded Anandakendra home content and {len(keep_ids)} running kendras.'))
