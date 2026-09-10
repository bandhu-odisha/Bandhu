"""seed_publications_content: offline, idempotent, and self-healing."""

import io
import os
import shutil
import tempfile
import urllib.error
from datetime import datetime
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from applications.publications.management.commands import seed_publications_content as seed
from applications.publications.models import HomePage, Publication
from bandhuapp.tests.support import TempMediaMixin, TINY_GIF

OFFLINE = mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline'))


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return TINY_GIF


def run_seed():
    out = io.StringIO()
    call_command('seed_publications_content', stdout=out)
    return out.getvalue()


class SeedPublicationsContentTests(TempMediaMixin, TestCase):
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

    def test_offline_seed_creates_homepage_and_publications(self):
        # TempMediaMixin's media_dir is shared for the whole test class (setUpClass), and
        # test_download_and_local_copy_paths (runs first alphabetically) writes CARD_PICTURE
        # into it. Use a private, empty MEDIA_ROOT so "urlopen gets called" doesn't depend on
        # alphabetical test execution order within the class.
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with OFFLINE as urlopen, override_settings(MEDIA_ROOT=empty_media_dir):
            output = run_seed()
        self.assertTrue(urlopen.called)

        home = HomePage.objects.get()
        self.assertEqual(home.picture.name, seed.CARD_PICTURE)
        self.assertEqual(Publication.objects.count(), len(seed.PUBLICATIONS))
        first = Publication.objects.get(slug='annual-report-24-2025')
        self.assertEqual(first.title, 'Annual Report 24-2025')
        self.assertTrue(first.is_visible)
        self.assertIsNone(first.by)
        self.assertEqual(first.created, timezone.make_aware(datetime(2025, 11, 6, 12, 0, 0)))
        self.assertEqual(first.media.name, 'publications/Bandhu_fLrWRJJ.pdf')
        self.assertIn(f'{len(seed.PUBLICATIONS)} publication(s)', output)
        # No files could be fetched, so nothing landed in MEDIA_ROOT.
        self.assertFalse(os.path.exists(os.path.join(empty_media_dir, seed.CARD_PICTURE)))

    def test_download_and_local_copy_paths(self):
        img_dir = os.path.join(self.base_dir, 'img')
        os.makedirs(img_dir, exist_ok=True)
        with open(os.path.join(img_dir, 'our_mission.jpg'), 'wb') as handle:
            handle.write(TINY_GIF)
        with mock.patch('urllib.request.urlopen', return_value=FakeResponse()) as urlopen:
            run_seed()
        os.remove(os.path.join(img_dir, 'our_mission.jpg'))

        # Card picture came from the local img/ tree; the rest were "downloaded".
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, seed.CARD_PICTURE)))
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'publications', 'Bandhu_fLrWRJJ.pdf')))
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'publications', 'thumb', 'Paika2015_GLepb7k.jpeg')))
        # The Paika 2015 thumb is fetched from its live (non-thumb) path.
        requested = [call.args[0].full_url for call in urlopen.call_args_list]
        self.assertIn('https://bandhuodisha.in/media/publications/Paika2015_GLepb7k.jpeg', requested)
        self.assertNotIn('https://bandhuodisha.in/media/' + seed.CARD_PICTURE, requested)

    def test_seed_is_idempotent_and_prunes_unknown_slugs(self):
        Publication.objects.create(
            slug='stray', title='Stray', description='d', created=timezone.now(),
            thumb='t.gif', media='m.pdf',
        )
        with OFFLINE:
            run_seed()
            counts = (HomePage.objects.count(), Publication.objects.count())
            edited = Publication.objects.get(slug='paika-2019')
            edited.title = 'Edited'
            edited.is_visible = False
            edited.save()
            run_seed()
        self.assertEqual((HomePage.objects.count(), Publication.objects.count()), counts)
        self.assertFalse(Publication.objects.filter(slug='stray').exists())
        edited.refresh_from_db()
        self.assertEqual(edited.title, 'Paika 2019')
        self.assertTrue(edited.is_visible)

    def test_existing_homepage_without_picture_gets_card_when_file_available(self):
        home = HomePage.objects.create(tagline='Keep me', description='desc', picture='')
        with mock.patch('urllib.request.urlopen', return_value=FakeResponse()):
            run_seed()
        home.refresh_from_db()
        self.assertEqual(home.tagline, 'Keep me')
        self.assertEqual(home.picture.name, seed.CARD_PICTURE)

    def test_existing_homepage_keeps_custom_picture(self):
        home = HomePage.objects.create(tagline='Keep me', description='desc', picture='custom/pic.jpg')
        with mock.patch('urllib.request.urlopen', return_value=FakeResponse()):
            run_seed()
        home.refresh_from_db()
        self.assertEqual(home.picture.name, 'custom/pic.jpg')
        self.assertEqual(HomePage.objects.count(), 1)
