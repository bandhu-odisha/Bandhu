import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.swabalamban.models import CarouselImage, HomePage, Product

SWABALAMBAN_INTRO = (
    'Swabalamban strives to revive the spirit of our villages and check, rather reverse, '
    'the mindless migration to cities. Processing units for farm products are set up in '
    'rural areas to ensure the financial stability of farmers, and youth are assisted to '
    'become self-sustainable financially.'
)

SWABALAMBAN_TAGLINE = 'In the village and by the villagers...'

CAPTION_EN = '"Self-reliance blossoms when villages shape their own path."'
CAPTION_OR = '"ଗାଁ ନିଜ ପଥ ନିଜେ ଗଢିଲେ ସ୍ୱାବଳମ୍ବନ ଫୁଲିଉଠେ।"'

ORDER_NOTE = (
    'Explore our products below for quality produce. If you want to place an order, '
    'contact us on WhatsApp at <strong>+91 00000 00000</strong>.'
)

PRODUCTS = [
    {
        'name': 'Premium Moong Dal',
        'image_file': 'moong',
        'label': 'Premium Moong Dal',
        'source_image': 'MOOONG.jpg',
        'intro_lead': 'Yellow Split Mung Beans.',
        'intro_text': (
            'Carefully sourced from our farmers and naturally processed. Made by splitting and '
            'de-husking premium quality green mung beans. Mild flavor and smooth texture; cooks '
            'quickly and blends into a variety of dishes.'
        ),
        'nutritional_highlights': '\n'.join([
            'High plant-based protein',
            'Rich in dietary fiber',
            'Easy to digest',
            'Supports healthy metabolism',
            'Ideal for soups, stews, baby food & traditional recipes',
        ]),
        'quality_promise': '\n'.join([
            'Farm-direct sourcing',
            'Naturally sun-dried',
            'Hygienically cleaned',
            'No artificial polishing',
        ]),
        'sort_order': 1,
    },
    {
        'name': 'Premium Whole Green Moong',
        'image_file': 'green',
        'label': 'Premium Whole Green Moong',
        'source_image': 'green moong.jpg',
        'intro_lead': '',
        'intro_text': (
            'Carefully harvested and sun-dried without removing the outer skin to preserve '
            'maximum nutrition. Ideal for sprouting, traditional curries, and health-focused meals.'
        ),
        'nutritional_highlights': '\n'.join([
            'Rich in antioxidants',
            'High in protein & fiber',
            'Supports weight management',
            'Excellent for sprouting',
        ]),
        'quality_promise': '\n'.join([
            'Farm-to-table sourcing',
            'No artificial polish',
            'Retains natural color & nutrients',
            'Freshly packed',
        ]),
        'sort_order': 2,
    },
    {
        'name': 'Premium Black Dal',
        'image_file': 'black',
        'label': 'Premium Black Dal',
        'source_image': 'black dal.jpg',
        'intro_lead': 'Urad beans.',
        'intro_text': (
            'Grown in nutrient-rich soil and harvested at peak maturity. Rich, earthy flavor and '
            'creamy texture when cooked. Carefully cleaned and minimally processed to retain natural goodness.'
        ),
        'nutritional_highlights': '\n'.join([
            'Excellent source of protein',
            'Naturally rich in iron & calcium',
            'Supports bone and muscle health',
            'Provides sustained energy',
        ]),
        'quality_promise': '\n'.join([
            'Traditional farming practices',
            'Sun-dried',
            'Chemical residue tested',
            'Export-grade sorting',
        ]),
        'sort_order': 3,
    },
    {
        'name': 'Premium Red Lentils (Masoor Dal)',
        'image_file': 'red',
        'label': 'Premium Red Lentils (Masoor Dal)',
        'source_image': 'red dal.jpg',
        'intro_lead': '',
        'intro_text': (
            'Obtained by gently de-husking and splitting mature masoor beans. Vibrant color and quick '
            'cooking; smooth consistency and rich taste.'
        ),
        'nutritional_highlights': '\n'.join([
            'High protein & fiber',
            'Supports heart health',
            'Good source of iron',
            'Easy to cook and digest',
        ]),
        'quality_promise': '\n'.join([
            'Naturally cultivated',
            'Uniform size grading',
            'Cleaned & packed under hygienic conditions',
        ]),
        'sort_order': 4,
    },
]


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
        hero_path = 'swabalamban/carousel/pimg2.jpg'
        self._ensure_image(
            hero_path,
            'pimg2.jpg',
            remote_media_paths=(
                'swabalamban/carousel/pimg2.jpg',
                'bandhuapp/swabalamban/pimg2.jpg',
            ),
        )

        homepage = HomePage.objects.first()
        if not homepage:
            homepage = HomePage(
                tagline=SWABALAMBAN_TAGLINE,
                description=SWABALAMBAN_INTRO,
                caption_en=CAPTION_EN,
                caption_or=CAPTION_OR,
                order_note=ORDER_NOTE,
                whatsapp_number='+91 00000 00000',
                products_heading='Quality produce from our Swabalamban initiative.',
            )
        homepage.tagline = SWABALAMBAN_TAGLINE
        homepage.description = SWABALAMBAN_INTRO
        homepage.caption_en = CAPTION_EN
        homepage.caption_or = CAPTION_OR
        homepage.order_note = ORDER_NOTE
        homepage.whatsapp_number = '+91 00000 00000'
        homepage.products_heading = 'Quality produce from our Swabalamban initiative.'
        if self._ensure_image(
            hero_path,
            'pimg2.jpg',
            remote_media_paths=(
                'swabalamban/carousel/pimg2.jpg',
                'bandhuapp/swabalamban/pimg2.jpg',
            ),
        ):
            homepage.picture = hero_path
            homepage.banner_image = hero_path
        homepage.save()

        CarouselImage.objects.all().delete()
        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, hero_path)):
            CarouselImage.objects.create(picture=hero_path, sort_order=0)

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

        Product.objects.exclude(id__in=kept_ids).delete()
        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded Swabalamban homepage and {len(kept_ids)} product(s).'
            )
        )
