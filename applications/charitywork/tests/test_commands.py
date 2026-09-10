"""Tests for the seed_charitywork_content management command (no network)."""

import os
import shutil
import tempfile
import urllib.error
from datetime import date
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from applications.charitywork.management.commands import seed_charitywork_content as cmd
from applications.charitywork.models import Charity, HomePage
from bandhuapp.tests.support import TempMediaMixin, image_upload

URLOPEN = 'urllib.request.urlopen'


def fake_urlopen(*args, **kwargs):
    response = mock.MagicMock()
    response.__enter__.return_value.read.return_value = b'image-bytes'
    return response


def run():
    out = StringIO()
    call_command('seed_charitywork_content', stdout=out)
    return out.getvalue()


def make_charity(**overrides):
    data = dict(
        title='Old', purpose='p', location='loc', description='d', slug='old',
        image=image_upload(),
    )
    data.update(overrides)
    return Charity.objects.create(**data)


class SeedOfflineTests(TempMediaMixin, TestCase):
    def setUp(self):
        patcher = mock.patch(URLOPEN, side_effect=urllib.error.URLError('offline'))
        self.urlopen = patcher.start()
        self.addCleanup(patcher.stop)

    def test_seeds_homepage_and_charities(self):
        # TempMediaMixin's media_dir is shared for the whole class (setUpClass), and sibling
        # tests in this class create Charity rows with image_upload(), which really writes
        # files into it. Use a private, empty MEDIA_ROOT here so "nothing was downloaded"
        # doesn't depend on alphabetical test execution order.
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with override_settings(MEDIA_ROOT=empty_media_dir):
            output = run()
        self.assertIn('2 activity card(s)', output)
        self.assertTrue(self.urlopen.called)

        homepage = HomePage.objects.get(pk=1)
        self.assertEqual(homepage.tagline, cmd.TAGLINE)
        self.assertEqual(homepage.description, cmd.DESCRIPTION)
        self.assertEqual(homepage.picture.name, cmd.HOMEPAGE_PICTURE)
        self.assertTrue(homepage.image_caption_en)

        self.assertEqual(Charity.objects.count(), 2)
        first = Charity.objects.get(slug=cmd.CHARITIES[0]['slug'])
        self.assertEqual(first.start_date, date(2020, 8, 17))
        self.assertEqual(first.image.name, cmd.CHARITIES[0]['image'])
        for root, _dirs, files in os.walk(empty_media_dir):
            self.assertEqual(files, [], root)

    def test_idempotent_and_prunes_unlisted(self):
        run()
        stray = make_charity()
        run()
        self.assertEqual(Charity.objects.count(), 2)
        self.assertFalse(Charity.objects.filter(pk=stray.pk).exists())
        self.assertEqual(HomePage.objects.count(), 1)

    def test_matches_existing_by_slug_or_title_and_location(self):
        row0, row1 = cmd.CHARITIES
        by_slug = make_charity(slug=row0['slug'], title='Renamed', location='Elsewhere')
        by_title = make_charity(slug='legacy', title=row1['title'], location=row1['location'])
        HomePage.objects.create(pk=1, tagline='x', description='y', image_caption_or='Keep')
        run()
        by_slug.refresh_from_db()
        by_title.refresh_from_db()
        self.assertEqual(by_slug.title, row0['title'])
        self.assertEqual(by_slug.location, row0['location'])
        self.assertEqual(by_title.slug, row1['slug'])
        self.assertEqual(by_title.purpose, row1['purpose'])
        self.assertEqual(Charity.objects.count(), 2)
        self.assertEqual(HomePage.objects.get(pk=1).image_caption_or, 'Keep')


class SeedDownloadTests(TempMediaMixin, TestCase):
    def test_downloads_files_once(self):
        with mock.patch(URLOPEN, side_effect=fake_urlopen) as urlopen:
            run()
        self.assertEqual(urlopen.call_count, 3)
        for rel in [cmd.HOMEPAGE_PICTURE] + [row['image'] for row in cmd.CHARITIES]:
            path = os.path.join(self.media_dir, rel)
            self.assertTrue(os.path.isfile(path), rel)
            with open(path, 'rb') as f:
                self.assertEqual(f.read(), b'image-bytes')
        with mock.patch(URLOPEN, side_effect=fake_urlopen) as urlopen:
            run()
        self.assertFalse(urlopen.called)


class SeedLocalCopyTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-')
        self.addCleanup(shutil.rmtree, self.base_dir, True)
        img_dir = os.path.join(self.base_dir, 'img')
        os.makedirs(img_dir)
        for rel in [cmd.HOMEPAGE_PICTURE] + [row['image'] for row in cmd.CHARITIES]:
            with open(os.path.join(img_dir, os.path.basename(rel)), 'wb') as handle:
                handle.write(b'local')

    def test_copies_local_sources_without_network(self):
        with override_settings(BASE_DIR=self.base_dir), \
                mock.patch(URLOPEN, side_effect=AssertionError('network used')):
            run()
        for rel in [cmd.HOMEPAGE_PICTURE] + [row['image'] for row in cmd.CHARITIES]:
            with open(os.path.join(self.media_dir, rel), 'rb') as f:
                self.assertEqual(f.read(), b'local')
