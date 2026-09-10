"""seed_swabalamban_content: offline, idempotent, never writes outside the temp tree."""

import io
import os
import shutil
import tempfile
import urllib.error
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from applications.swabalamban.management.commands import seed_swabalamban_content as seed
from applications.swabalamban.models import Product
from bandhuapp.models import SwabalambanHomePage, SwabalambanHomePhoto
from bandhuapp.tests.support import TempMediaMixin, TINY_GIF

OFFLINE = mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline'))


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return TINY_GIF


def run_seed(*args):
    out = io.StringIO()
    call_command('seed_swabalamban_content', *args, stdout=out)
    return out.getvalue()


class SeedSwabalambanContentTests(TempMediaMixin, TestCase):
    """BASE_DIR is redirected because the command mirrors media into BASE_DIR/static/img."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-')
        cls._base_override = override_settings(BASE_DIR=cls.base_dir)
        cls._base_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._base_override.disable()
        super().tearDownClass()

    def _put_img(self, name, root='img'):
        directory = os.path.join(self.base_dir, root)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name)
        with open(path, 'wb') as handle:
            handle.write(TINY_GIF)
        return path

    def test_offline_seed_without_images_still_creates_page_and_products(self):
        # BASE_DIR and MEDIA_ROOT are shared for the whole test class (setUpClass), and
        # sibling tests (_put_img) really write local img sources into them. Use private,
        # empty dirs here so "no images available" doesn't depend on alphabetical test
        # execution order within the class.
        empty_base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-empty-')
        self.addCleanup(shutil.rmtree, empty_base_dir, True)
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with OFFLINE as urlopen, \
                override_settings(BASE_DIR=empty_base_dir, MEDIA_ROOT=empty_media_dir):
            output = run_seed()
        self.assertTrue(urlopen.called)

        page = SwabalambanHomePage.objects.get()
        self.assertEqual(page.tagline, seed.SWABALAMBAN_TAGLINE)
        self.assertEqual(page.description, seed.SWABALAMBAN_INTRO)
        self.assertEqual(page.whatsapp_number, seed.WHATSAPP_NUMBER)
        self.assertEqual(page.image_caption_or, seed.CAPTION_OR)
        self.assertFalse(page.hero_image)
        self.assertEqual(SwabalambanHomePhoto.objects.count(), 0)

        self.assertEqual(Product.objects.count(), len(seed.PRODUCTS))
        moong = Product.objects.get(name='Premium Moong Dal')
        self.assertEqual(moong.sort_order, 1)
        self.assertFalse(moong.image)
        self.assertEqual(moong.highlight_list[0], 'High plant-based protein')
        self.assertIn('Missing source image: MOOONG.jpg', output)
        self.assertIn('0 gallery photo(s)', output)
        self.assertIn(f'{len(seed.PRODUCTS)} catalog product(s)', output)
        self.assertFalse(os.path.exists(os.path.join(empty_base_dir, 'static', 'img')))

    def test_local_sources_are_copied_mirrored_and_linked(self):
        self._put_img('swamblamban_1.jpg')                 # BASE_DIR/img
        self._put_img('pimg2.jpg', root=os.path.join('static', 'img'))  # BASE_DIR/static/img
        media_src = os.path.join(self.media_dir, 'bandhuapp', 'swabalamban')
        os.makedirs(media_src, exist_ok=True)
        with open(os.path.join(media_src, 'pimg3.jpg'), 'wb') as handle:  # already in MEDIA_ROOT
            handle.write(TINY_GIF)
        self._put_img('MOOONG.jpg')

        with OFFLINE:
            output = run_seed()

        page = SwabalambanHomePage.objects.get()
        self.assertEqual(page.hero_image.name, 'bandhuapp/swabalamban/swamblamban_1.jpg')
        photos = list(SwabalambanHomePhoto.objects.filter(page=page).order_by('sort_order'))
        self.assertEqual(
            [p.picture.name for p in photos],
            ['bandhuapp/swabalamban/swamblamban_1.jpg', 'bandhuapp/swabalamban/pimg2.jpg',
             'bandhuapp/swabalamban/pimg3.jpg'],
        )
        self.assertEqual([p.sort_order for p in photos], [0, 1, 2])
        self.assertIn('3 gallery photo(s)', output)
        self.assertIn('Missing source image: pimg6.jpg', output)

        moong = Product.objects.get(name='Premium Moong Dal')
        self.assertEqual(moong.image.name, 'swabalamban/products/moong.jpg')
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'swabalamban', 'products', 'moong.jpg')))
        # Media files are mirrored into BASE_DIR/static/img (the temp tree, not the repo).
        static_img = os.path.join(self.base_dir, 'static', 'img')
        for name in ('swamblamban_1.jpg', 'pimg3.jpg', 'MOOONG.jpg'):
            self.assertTrue(os.path.isfile(os.path.join(static_img, name)), name)

    def test_remote_download_falls_back_across_candidate_urls(self):
        # BASE_DIR and MEDIA_ROOT are shared for the whole test class (setUpClass), and
        # earlier-running sibling tests (_put_img) really write 'swamblamban_1.jpg' into
        # BASE_DIR/img. That local copy would short-circuit _ensure_image before it ever
        # tries the remote candidate URLs this test exists to exercise, so use private,
        # empty dirs to make the remote fallback path actually run regardless of test order.
        empty_base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-empty-')
        self.addCleanup(shutil.rmtree, empty_base_dir, True)
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)

        calls = []

        def fake_urlopen(req, timeout=None):
            calls.append(req.full_url)
            # Fail the first ("bandhuapp/swabalamban/...") candidate for the hero image and
            # for pimg2.jpg, so _ensure_image's remote loop actually advances to its second
            # candidate (the .png hero variant / the "swabalamban/carousel/" gallery path).
            if req.full_url.endswith('swamblamban_1.jpg'):
                raise urllib.error.URLError('first candidate missing')
            if req.full_url == 'https://bandhuodisha.in/media/bandhuapp/swabalamban/pimg2.jpg':
                raise urllib.error.URLError('first candidate missing')
            return FakeResponse()

        with mock.patch('urllib.request.urlopen', side_effect=fake_urlopen), \
                override_settings(BASE_DIR=empty_base_dir, MEDIA_ROOT=empty_media_dir):
            run_seed()

        self.assertIn('https://bandhuodisha.in/media/bandhuapp/swabalamban/swamblamban_1.png', calls)
        self.assertIn('https://bandhuodisha.in/media/swabalamban/carousel/pimg2.jpg', calls)
        page = SwabalambanHomePage.objects.get()
        self.assertEqual(page.hero_image.name, 'bandhuapp/swabalamban/swamblamban_1.jpg')
        self.assertEqual(SwabalambanHomePhoto.objects.count(), len(seed.GALLERY_PHOTOS))
        # Products have no remote candidates, so their images stay unset offline.
        self.assertFalse(Product.objects.get(name='Premium Black Dal').image)

    def test_idempotent_updates_existing_page_photo_order_and_products(self):
        self._put_img('swamblamban_1.jpg')
        self._put_img('pimg2.jpg')
        page = SwabalambanHomePage.objects.create(tagline='old', description='old')
        SwabalambanHomePhoto.objects.create(page=page, picture='bandhuapp/swabalamban/pimg2.jpg', sort_order=7)
        SwabalambanHomePhoto.objects.create(page=page, picture='bandhuapp/swabalamban/stale.jpg', sort_order=9)
        Product.objects.create(name='Premium Moong Dal', label='old label', image='x.gif', intro_text='old', sort_order=42)

        with OFFLINE:
            run_seed()
            counts = (SwabalambanHomePage.objects.count(), SwabalambanHomePhoto.objects.count(), Product.objects.count())
            run_seed()

        self.assertEqual(
            (SwabalambanHomePage.objects.count(), SwabalambanHomePhoto.objects.count(), Product.objects.count()),
            counts,
        )
        page.refresh_from_db()
        self.assertEqual(page.tagline, seed.SWABALAMBAN_TAGLINE)
        self.assertEqual(page.products_heading, seed.PRODUCTS_HEADING)
        self.assertFalse(SwabalambanHomePhoto.objects.filter(picture='bandhuapp/swabalamban/stale.jpg').exists())
        self.assertEqual(SwabalambanHomePhoto.objects.get(picture='bandhuapp/swabalamban/pimg2.jpg').sort_order, 1)
        moong = Product.objects.get(name='Premium Moong Dal')
        self.assertEqual(moong.sort_order, 1)
        self.assertEqual(moong.label, 'Premium Moong Dal')
        self.assertEqual(moong.image.name, 'x.gif')  # no seed image available → untouched

    def test_prune_products_flag_removes_rows_outside_catalog(self):
        Product.objects.create(name='Custom', label='c', image='x.gif', intro_text='t')
        with OFFLINE:
            run_seed()
        self.assertTrue(Product.objects.filter(name='Custom').exists())
        with OFFLINE:
            run_seed('--prune-products')
        self.assertFalse(Product.objects.filter(name='Custom').exists())
        self.assertEqual(Product.objects.count(), len(seed.PRODUCTS))
