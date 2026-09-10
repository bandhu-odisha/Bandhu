"""Tests for the seed_anandakendra_content management command (no network)."""

import os
import shutil
import tempfile
import urllib.error
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from applications.anandakendra.management.commands import seed_anandakendra_content as cmd
from applications.anandakendra.models import AnandaKendra, HomePage, Photo
from bandhuapp.tests.support import TempMediaMixin, image_upload

URLOPEN = 'urllib.request.urlopen'


def fake_urlopen(*args, **kwargs):
    response = mock.MagicMock()
    response.__enter__.return_value.read.return_value = b'image-bytes'
    return response


def run():
    out = StringIO()
    call_command('seed_anandakendra_content', stdout=out)
    return out.getvalue()


class SeedOfflineTests(TempMediaMixin, TestCase):
    """No local img/ source and downloads fail: DB content still seeded, no files written."""

    def setUp(self):
        patcher = mock.patch(URLOPEN, side_effect=urllib.error.URLError('offline'))
        self.urlopen = patcher.start()
        self.addCleanup(patcher.stop)

    def test_seeds_homepage_and_kendras_without_files(self):
        # TempMediaMixin's media_dir is shared for the whole class (setUpClass), and sibling
        # tests in this class create AnandaKendra rows with image_upload(), which really
        # writes files into it. Use a private, empty MEDIA_ROOT here so "nothing was
        # downloaded" doesn't depend on alphabetical test execution order.
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with override_settings(MEDIA_ROOT=empty_media_dir):
            output = run()
        self.assertIn('3 running kendras', output)
        self.assertIn('0 gallery photo(s)', output)
        self.assertIn('Missing gallery file', output)
        self.assertTrue(self.urlopen.called)

        homepage = HomePage.objects.get(pk=1)
        self.assertEqual(homepage.description, cmd.ANANDAKENDRA_INTRO)
        self.assertEqual(homepage.picture.name, 'anandakendra/index/clients-bg1.jpg')
        self.assertTrue(homepage.image_caption_en)

        self.assertEqual(AnandaKendra.objects.count(), 3)
        self.assertEqual(
            set(AnandaKendra.objects.values_list('slug', flat=True)),
            {row['slug'] for row in cmd.RUNNING_KENDRAS},
        )
        self.assertEqual(Photo.objects.count(), 0)
        # Nothing was downloaded into MEDIA_ROOT (directories may be pre-created).
        for root, _dirs, files in os.walk(empty_media_dir):
            self.assertEqual(files, [], root)

    def test_idempotent_and_prunes_unlisted_kendras(self):
        run()
        stray = AnandaKendra.objects.create(
            name='Stray', locality='Nowhere', slug='stray', description='d', address='a',
            image=image_upload(),
        )
        Photo.objects.create(kendra=stray, picture=image_upload(), approved=True)
        run()
        self.assertEqual(AnandaKendra.objects.count(), 3)
        self.assertFalse(AnandaKendra.objects.filter(pk=stray.pk).exists())
        self.assertEqual(HomePage.objects.count(), 1)

    def test_existing_kendra_keeps_custom_address_and_captions(self):
        row = cmd.RUNNING_KENDRAS[0]
        kendra = AnandaKendra.objects.create(
            name=row['name'], locality=row['locality'], slug='old-slug',
            description='old', address='Custom address', image=image_upload(),
        )
        blank = cmd.RUNNING_KENDRAS[1]
        AnandaKendra.objects.create(
            name=blank['name'], locality=blank['locality'], slug='other-old',
            description='old', address='   ', image=image_upload(),
        )
        HomePage.objects.create(pk=1, tagline='x', description='y', image_caption_en='Keep me')
        run()
        kendra.refresh_from_db()
        self.assertEqual(kendra.slug, row['slug'])
        self.assertEqual(kendra.description, row['description'])
        self.assertEqual(kendra.address, 'Custom address')
        self.assertEqual(kendra.image.name, row['image'])
        self.assertEqual(
            AnandaKendra.objects.get(name=blank['name'], locality=blank['locality']).address,
            blank['locality'],
        )
        homepage = HomePage.objects.get(pk=1)
        self.assertEqual(homepage.image_caption_en, 'Keep me')
        self.assertEqual(homepage.tagline, '')


class SeedDownloadTests(TempMediaMixin, TestCase):
    """Downloads succeed (mocked): files land in MEDIA_ROOT and gallery photos are synced."""

    def test_downloads_files_and_syncs_gallery(self):
        with mock.patch(URLOPEN, side_effect=fake_urlopen) as urlopen:
            output = run()
        self.assertTrue(urlopen.called)
        expected_photos = sum(len(v) for v in cmd.KENDRA_GALLERY_IMAGES.values())
        self.assertIn(f'{expected_photos} gallery photo(s)', output)
        self.assertEqual(Photo.objects.count(), expected_photos)
        self.assertTrue(Photo.objects.filter(approved=False).count() == 0)
        for row in cmd.RUNNING_KENDRAS:
            self.assertTrue(os.path.isfile(os.path.join(self.media_dir, row['image'])))
        for paths in cmd.KENDRA_GALLERY_IMAGES.values():
            for rel in paths:
                self.assertTrue(os.path.isfile(os.path.join(self.media_dir, rel)))

        # Second run: files already exist, so no new download; photo rows reused.
        first_ids = set(Photo.objects.values_list('id', flat=True))
        with mock.patch(URLOPEN, side_effect=fake_urlopen) as urlopen:
            run()
        self.assertFalse(urlopen.called)
        self.assertEqual(set(Photo.objects.values_list('id', flat=True)), first_ids)

    def test_gallery_sync_removes_stale_photos(self):
        with mock.patch(URLOPEN, side_effect=fake_urlopen):
            run()
        kendra = AnandaKendra.objects.get(slug='anandakendra-1-jabalpur')
        stale = Photo.objects.create(kendra=kendra, picture=image_upload('stale.gif'))
        with mock.patch(URLOPEN, side_effect=fake_urlopen):
            run()
        self.assertFalse(Photo.objects.filter(pk=stale.pk).exists())
        self.assertEqual(Photo.objects.filter(kendra=kendra).count(),
                         len(cmd.KENDRA_GALLERY_IMAGES[kendra.slug]))


class SeedLocalCopyTests(TempMediaMixin, TestCase):
    """A local <BASE_DIR>/img/<basename> is copied instead of downloaded."""

    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)
        img_dir = os.path.join(self.base_dir, 'img')
        os.makedirs(img_dir)
        names = {'clients-bg1.jpg'}
        names.update(os.path.basename(row['image']) for row in cmd.RUNNING_KENDRAS)
        for paths in cmd.KENDRA_GALLERY_IMAGES.values():
            names.update(os.path.basename(p) for p in paths)
        for name in names:
            with open(os.path.join(img_dir, name), 'wb') as handle:
                handle.write(b'local')

    def test_copies_local_sources_without_network(self):
        with override_settings(BASE_DIR=self.base_dir), \
                mock.patch(URLOPEN, side_effect=AssertionError('network used')):
            output = run()
        self.assertIn('running kendras', output)
        with open(os.path.join(self.media_dir, 'anandakendra/index/clients-bg1.jpg'), 'rb') as f:
            self.assertEqual(f.read(), b'local')
        for row in cmd.RUNNING_KENDRAS:
            self.assertTrue(os.path.isfile(os.path.join(self.media_dir, row['image'])))
        expected_photos = sum(len(v) for v in cmd.KENDRA_GALLERY_IMAGES.values())
        self.assertEqual(Photo.objects.count(), expected_photos)
