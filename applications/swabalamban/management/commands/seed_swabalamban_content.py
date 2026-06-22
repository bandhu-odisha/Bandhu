import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.swabalamban.models import CarouselImage, HomePage, Product
from bandhuapp.models import Mission, SwabalambanCarousel

SWABALAMBAN_INTRO = (
    'Swabalamban strives to revive the spirit of our villages and check, rather reverse, '
    'the mindless migration to cities. Processing units for farm products like paddy, '
    'cereals, oilseeds are set up in rural areas to ensure the financial stability of '
    'farmers. Youth are assisted to become self-sustainable financially.'
)

SWABALAMBAN_TAGLINE = 'In the village and by the villagers...'

CAPTION_EN = '"Self-reliance blossoms when villages shape their own path."'
CAPTION_OR = '"ଗାଁ ନିଜ ପଥ ନିଜେ ଗଢିଲେ ସ୍ୱାବଳମ୍ବନ ଫୁଲିଉଠେ।"'

ORDER_NOTE = ''

PRODUCTS = []


class Command(BaseCommand):
    help = 'Seed Swabalamban homepage copy, carousel image, and product catalog.'

    def _ensure_image(self, relative_media_path, source_name, remote_media_paths=()):
        destination = os.path.join(settings.MEDIA_ROOT, relative_media_path)
        if os.path.isfile(destination):
            self._mirror_to_static_img(source_name, destination)
            return True

        for root in (
            os.path.join(settings.BASE_DIR, 'img'),
            os.path.join(settings.BASE_DIR, 'static', 'img'),
            os.path.join(settings.MEDIA_ROOT, 'bandhuapp', 'swabalamban'),
        ):
            source = os.path.join(root, source_name)
            if os.path.isfile(source):
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                shutil.copy2(source, destination)
                self._mirror_to_static_img(source_name, destination)
                return True

        for remote_path in remote_media_paths:
            url = f'https://bandhuodisha.in/media/{remote_path}'
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Referer': 'https://bandhuodisha.in/swabalamban/',
                    },
                )
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                with urllib.request.urlopen(req, timeout=30) as response:
                    with open(destination, 'wb') as handle:
                        handle.write(response.read())
                self._mirror_to_static_img(source_name, destination)
                return True
            except (urllib.error.URLError, OSError):
                continue

        self.stdout.write(self.style.WARNING(f'Missing source image: {source_name}'))
        return False

    def _mirror_to_static_img(self, source_name, media_file):
        static_img_dir = os.path.join(settings.BASE_DIR, 'static', 'img')
        static_dest = os.path.join(static_img_dir, source_name)
        if os.path.isfile(static_dest):
            return
        os.makedirs(static_img_dir, exist_ok=True)
        shutil.copy2(media_file, static_dest)

    def handle(self, *args, **options):
        hero_path = 'bandhuapp/swabalamban/swamblamban_1.jpg'
        self._ensure_image(
            hero_path,
            'swamblamban_1.jpg',
            remote_media_paths=(
                'bandhuapp/swabalamban/swamblamban_1.jpg',
                'bandhuapp/swabalamban/swamblamban_1.png',
            ),
        )

        homepage, _created = HomePage.objects.get_or_create(
            pk=1,
            defaults={
                'tagline': SWABALAMBAN_TAGLINE,
                'description': SWABALAMBAN_INTRO,
                'caption_en': CAPTION_EN,
                'caption_or': CAPTION_OR,
                'order_note': ORDER_NOTE,
                'whatsapp_number': '',
                'products_heading': 'Quality produce from our Swabalamban initiative.',
            },
        )
        homepage.tagline = SWABALAMBAN_TAGLINE
        homepage.description = SWABALAMBAN_INTRO
        homepage.caption_en = CAPTION_EN
        homepage.caption_or = CAPTION_OR
        homepage.order_note = ORDER_NOTE
        homepage.whatsapp_number = ''
        homepage.products_heading = 'Quality produce from our Swabalamban initiative.'
        if self._ensure_image(
            hero_path,
            'swamblamban_1.jpg',
            remote_media_paths=(
                'bandhuapp/swabalamban/swamblamban_1.jpg',
                'bandhuapp/swabalamban/swamblamban_1.png',
            ),
        ):
            homepage.picture = hero_path
            homepage.banner_image = hero_path
        homepage.save()

        CarouselImage.objects.all().delete()
        carousel_path = hero_path
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, carousel_path)):
            CarouselImage.objects.create(picture=carousel_path, sort_order=0)

        mission = Mission.objects.first()
        if mission:
            mission.swabalamban_tagline = SWABALAMBAN_TAGLINE
            mission.swabalamban_desc = SWABALAMBAN_INTRO
            mission.save(update_fields=['swabalamban_tagline', 'swabalamban_desc'])
            SwabalambanCarousel.objects.filter(mission=mission).delete()
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, carousel_path)):
                SwabalambanCarousel.objects.create(mission=mission, picture=carousel_path)

        kept_ids = []
        for row in PRODUCTS:
            media_path = f"swabalamban/products/{row['image_file']}.jpg"
            self._ensure_image(media_path, row['source_image'])
            defaults = {
                'name': row['name'],
                'label': row['label'],
                'intro_lead': row['intro_lead'],
                'intro_text': row['intro_text'],
                'nutritional_highlights': row['nutritional_highlights'],
                'quality_promise': row['quality_promise'],
                'sort_order': row['sort_order'],
                'is_published': True,
            }
            if os.path.isfile(os.path.join(settings.MEDIA_ROOT, media_path)):
                defaults['image'] = media_path

            product, _created = Product.objects.update_or_create(
                name=row['name'],
                defaults=defaults,
            )
            kept_ids.append(product.id)

        if kept_ids:
            Product.objects.exclude(id__in=kept_ids).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded Swabalamban homepage copy and carousel; {len(kept_ids)} product(s) synced.'
            )
        )
