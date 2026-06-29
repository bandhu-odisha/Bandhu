import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from bandhuapp.models import SanskarHomePage, SanskarHomePhoto

SANSKAR_TAGLINE = 'Anandakendra and Ankurayan'

SANSKAR_DESC = (
    '<b>Anandakendra: </b>Anandakendra is conceived to support the children in '
    'villages for completing their school education successfully. Successfully, not only in '
    'terms of good marks in the examinations but also in terms of a sound understanding of '
    'fundamentals. More importantly, this initiative aims to ensure a supportive environment '
    'for an overall (personal-social-spiritual) development at a tender stage of life. We hope '
    'them to develop in themselves a keen fellow-feeling, a broader, deeper, and more practical '
    'outlook towards life, and a sincere urge to serve.  Anandakendra is not meant to be the '
    'replacement of a school but to take care of the children beyond the school hours.  '
    '<br>\n'
    '<b>Ankurayan: </b>Conceived as an annual festival of light and delight, it has '
    'been organised since 2006 and has now become a household name in some parts of coastal '
    'Odisha. This witnesses a gathering of more than 2000 students each year in mid-December at '
    'the bank of Paika, a distributary of Mahanadi separating the two districts-  Kendrapara and  '
    'Jagatsinghpur.'
)

CAPTION_EN = '"Learning with values lights every life and builds a brighter tomorrow."'
CAPTION_OR = '"ମୂଲ୍ୟ ସହିତ ଶିକ୍ଷା ପ୍ରତ୍ୟେକ ଜୀବନକୁ ଆଲୋକିତ କରେ ଏବଂ ଏକ ଉଜ୍ଜ୍ୱଳ ଭବିଷ୍ୟତ ଗଢେ।"'

HERO_IMAGE = ('bandhuapp/sanskar/collage_1.jpg', 'collage_1.jpg')

GALLERY_PHOTOS = (
    ('bandhuapp/sanskar/collage.jpg', 'collage.jpg'),
    ('bandhuapp/sanskar/pimg2.jpg', 'pimg2.jpg'),
    ('bandhuapp/sanskar/pimg3.jpg', 'pimg3.jpg'),
    ('bandhuapp/sanskar/pimg6.jpg', 'pimg6.jpg'),
)


class Command(BaseCommand):
    help = 'Seed Sanskar home page copy, hero image, and gallery photos.'

    def _ensure_image(self, relative_media_path, source_name, remote_media_paths=()):
        destination = os.path.join(settings.MEDIA_ROOT, relative_media_path)
        if os.path.isfile(destination):
            return True

        for root in (
            os.path.join(settings.BASE_DIR, 'img'),
            os.path.join(settings.BASE_DIR, 'static', 'img'),
            os.path.join(settings.MEDIA_ROOT, 'bandhuapp', 'sanskar'),
        ):
            source = os.path.join(root, source_name)
            if os.path.isfile(source):
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
                return True

        for remote_path in remote_media_paths:
            url = f'https://bandhuodisha.in/media/{remote_path}'
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': 'https://bandhuodisha.in/sanskar/',
                    },
                )
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                with urllib.request.urlopen(req, timeout=30) as response:
                    with open(destination, 'wb') as handle:
                        handle.write(response.read())
                return True
            except (urllib.error.URLError, OSError):
                continue

        self.stdout.write(self.style.WARNING(f'Missing source image: {source_name}'))
        return False

    def _sync_gallery(self, page):
        existing = {
            photo.picture.name: photo
            for photo in SanskarHomePhoto.objects.filter(page=page)
            if photo.picture and photo.picture.name
        }
        kept_ids = []
        for sort_order, (relative_path, source_name) in enumerate(GALLERY_PHOTOS):
            if not self._ensure_image(
                relative_path,
                source_name,
                remote_media_paths=(relative_path,),
            ):
                continue
            photo = existing.get(relative_path)
            if photo:
                if photo.sort_order != sort_order:
                    photo.sort_order = sort_order
                    photo.save(update_fields=['sort_order'])
            else:
                photo = SanskarHomePhoto.objects.create(
                    page=page,
                    picture=relative_path,
                    sort_order=sort_order,
                )
            kept_ids.append(photo.id)

        SanskarHomePhoto.objects.filter(page=page).exclude(id__in=kept_ids).delete()
        return kept_ids

    def handle(self, *args, **options):
        hero_path, hero_source = HERO_IMAGE
        self._ensure_image(hero_path, hero_source, remote_media_paths=(hero_path,))

        page = SanskarHomePage.objects.first()
        if not page:
            page = SanskarHomePage.objects.create(
                tagline=SANSKAR_TAGLINE,
                description=SANSKAR_DESC,
                image_caption_en=CAPTION_EN,
                image_caption_or=CAPTION_OR,
            )
        else:
            page.tagline = SANSKAR_TAGLINE
            page.description = SANSKAR_DESC
            page.image_caption_en = CAPTION_EN
            page.image_caption_or = CAPTION_OR
            page.save()

        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, hero_path)):
            page.hero_image = hero_path
            page.save(update_fields=['hero_image'])

        gallery_ids = self._sync_gallery(page)

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded Sanskar home page, hero image, and {len(gallery_ids)} gallery photo(s).'
            )
        )
