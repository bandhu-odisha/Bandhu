import os
import shutil
import urllib.error
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from applications.swabalamban.models import Product
from bandhuapp.models import SwabalambanHomePage, SwabalambanHomePhoto

SWABALAMBAN_INTRO = (
    'Swabalamban strives to revive the spirit of our villages and check, rather reverse, '
    'the mindless migration to cities. Processing units for farm products like paddy, '
    'cereals, oilseeds are set up in rural areas to ensure the financial stability of '
    'farmers. Youth are assisted to become self-sustainable financially.'
)

SWABALAMBAN_TAGLINE = 'In the village and by the villagers...'

CAPTION_EN = '"Self-reliance blossoms when villages shape their own path."'
CAPTION_OR = '"ଗାଁ ନିଜ ପଥ ନିଜେ ଗଢିଲେ ସ୍ୱାବଳମ୍ବନ ଫୁଲିଉଠେ।"'

WHATSAPP_NUMBER = '+91 94374 39371'

ORDER_NOTE = (
    'Explore our products below for quality produce. If you want to place an order, '
    f'contact us on WhatsApp at <strong>{WHATSAPP_NUMBER}</strong>.'
)

PRODUCTS_HEADING = 'Quality produce from our Swabalamban initiative.'

GALLERY_PHOTOS = (
    ('bandhuapp/swabalamban/swamblamban_1.jpg', 'swamblamban_1.jpg'),
    ('bandhuapp/swabalamban/pimg2.jpg', 'pimg2.jpg'),
    ('bandhuapp/swabalamban/pimg3.jpg', 'pimg3.jpg'),
    ('bandhuapp/swabalamban/pimg6.jpg', 'pimg6.jpg'),
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
    help = 'Seed Swabalamban home page copy, gallery images, and product catalog.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prune-products',
            action='store_true',
            help='Delete products that are not in the seed catalog.',
        )

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

    def _sync_gallery(self, page):
        existing = {
            photo.picture.name: photo
            for photo in SwabalambanHomePhoto.objects.filter(page=page)
            if photo.picture and photo.picture.name
        }
        kept_ids = []
        for sort_order, (relative_path, source_name) in enumerate(GALLERY_PHOTOS):
            remote_paths = (
                relative_path,
                relative_path.replace('bandhuapp/swabalamban/', 'swabalamban/carousel/'),
            )
            if not self._ensure_image(relative_path, source_name, remote_media_paths=remote_paths):
                continue
            photo = existing.get(relative_path)
            if photo:
                if photo.sort_order != sort_order:
                    photo.sort_order = sort_order
                    photo.save(update_fields=['sort_order'])
            else:
                photo = SwabalambanHomePhoto.objects.create(
                    page=page,
                    picture=relative_path,
                    sort_order=sort_order,
                )
            kept_ids.append(photo.id)

        SwabalambanHomePhoto.objects.filter(page=page).exclude(id__in=kept_ids).delete()
        return kept_ids

    def handle(self, *args, **options):
        hero_path = GALLERY_PHOTOS[0][0]
        self._ensure_image(
            hero_path,
            GALLERY_PHOTOS[0][1],
            remote_media_paths=(
                'bandhuapp/swabalamban/swamblamban_1.jpg',
                'bandhuapp/swabalamban/swamblamban_1.png',
            ),
        )

        page = SwabalambanHomePage.objects.first()
        if not page:
            page = SwabalambanHomePage.objects.create(
                tagline=SWABALAMBAN_TAGLINE,
                description=SWABALAMBAN_INTRO,
                image_caption_en=CAPTION_EN,
                image_caption_or=CAPTION_OR,
                order_note=ORDER_NOTE,
                whatsapp_number=WHATSAPP_NUMBER,
                products_heading=PRODUCTS_HEADING,
            )
        else:
            page.tagline = SWABALAMBAN_TAGLINE
            page.description = SWABALAMBAN_INTRO
            page.image_caption_en = CAPTION_EN
            page.image_caption_or = CAPTION_OR
            page.order_note = ORDER_NOTE
            page.whatsapp_number = WHATSAPP_NUMBER
            page.products_heading = PRODUCTS_HEADING
            page.save()

        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, hero_path)):
            page.hero_image = hero_path
            page.save(update_fields=['hero_image'])

        gallery_ids = self._sync_gallery(page)

        kept_ids = []
        for row in PRODUCTS:
            media_path = f"swabalamban/products/{row['image_file']}.jpg"
            self._ensure_image(media_path, row['source_image'])
            defaults = {
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

        if options['prune_products'] and kept_ids:
            Product.objects.exclude(id__in=kept_ids).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded Swabalamban home page, {len(gallery_ids)} gallery photo(s), '
                f'and {len(kept_ids)} catalog product(s).'
            )
        )
