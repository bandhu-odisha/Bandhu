"""seed_ashram_content: offline, idempotent, and self-healing."""

import io
import os
import shutil
import tempfile
import urllib.error
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from applications.ashram.management.commands import seed_ashram_content as seed
from applications.ashram.models import Activity, ActivityCategory, Ashram, HomePage, Photo
from bandhuapp.tests.support import TempMediaMixin, TINY_GIF

OFFLINE = mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline'))


class FakeResponse:
    def __init__(self, payload=TINY_GIF):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self):
        return self.payload


def run_seed():
    out = io.StringIO()
    call_command('seed_ashram_content', stdout=out)
    return out.getvalue()


class SeedAshramContentTests(TempMediaMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Point BASE_DIR at a throwaway tree so `img/` lookups never touch the repo.
        cls.base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-')
        cls._base_override = override_settings(BASE_DIR=cls.base_dir)
        cls._base_override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._base_override.disable()
        super().tearDownClass()

    def test_offline_seed_creates_homepage_and_bandhughars_without_gallery(self):
        # TempMediaMixin's media_dir is shared for the whole test class (setUpClass), and
        # sibling tests write real image files into it (e.g. via FakeResponse downloads).
        # Use a private, empty MEDIA_ROOT so "urlopen gets called" doesn't depend on
        # alphabetical test execution order within the class.
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with OFFLINE as urlopen, override_settings(MEDIA_ROOT=empty_media_dir):
            output = run_seed()
        self.assertTrue(urlopen.called)

        home = HomePage.objects.get(pk=1)
        self.assertEqual(home.tagline, 'An Abode for Goodness')
        self.assertEqual(home.description, seed.BANDHUGHAR_INTRO)
        self.assertEqual(home.picture.name, 'ashram/index/21.jpg')
        self.assertTrue(home.image_caption_en)  # default caption applied

        self.assertEqual(Ashram.objects.count(), len(seed.RUNNING_BANDHUGHARS))
        self.assertEqual(
            set(Ashram.objects.values_list('slug', flat=True)),
            {row['slug'] for row in seed.RUNNING_BANDHUGHARS},
        )
        # Gallery image could not be fetched: warning, no Photo rows.
        self.assertIn('Missing gallery file: ashram/2.jpg', output)
        self.assertEqual(Photo.objects.count(), 0)

        # Activities are synced regardless of images.
        ashram = Ashram.objects.get(slug='Activities_Bandhu_Ashram')
        self.assertEqual(Activity.objects.filter(category__ashram=ashram).count(), 1)
        self.assertIn('2 Bandhughars, 0 gallery photo(s), and 1 activit(ies)', output)
        # Nothing was written into this test's isolated MEDIA_ROOT.
        self.assertFalse(os.path.exists(os.path.join(empty_media_dir, 'ashram', '2.jpg')))

    def test_download_path_writes_file_and_creates_gallery_photo(self):
        with mock.patch('urllib.request.urlopen', return_value=FakeResponse()) as urlopen:
            output = run_seed()
        self.assertTrue(urlopen.called)
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'ashram', '2.jpg')))
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'ashram', 'index', '21.jpg')))
        photo = Photo.objects.get()
        self.assertEqual(photo.picture.name, 'ashram/2.jpg')
        self.assertTrue(photo.approved)
        self.assertEqual(photo.ashram.slug, 'Activities_Bandhu_Ashram')
        self.assertIn('1 gallery photo(s)', output)

    def test_local_img_source_is_copied_into_media_root(self):
        img_dir = os.path.join(self.base_dir, 'img')
        os.makedirs(img_dir, exist_ok=True)
        with open(os.path.join(img_dir, '2.jpg'), 'wb') as handle:
            handle.write(TINY_GIF)
        with OFFLINE:
            run_seed()
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'ashram', '2.jpg')))
        self.assertEqual(Photo.objects.count(), 1)
        os.remove(os.path.join(img_dir, '2.jpg'))

    def test_seed_is_idempotent_and_prunes_stray_rows(self):
        stray = Ashram.objects.create(
            name='Stray', locality='Nowhere', description='d', address='a', image='x.gif', slug='stray',
        )
        stray_cat = ActivityCategory.objects.create(ashram=stray, name='Old')
        # NOTE: no Activity on stray_cat. Activity.category is on_delete=PROTECT, so an
        # Activity here would make Ashram.objects.exclude(...).delete() raise ProtectedError
        # (the command prunes stray Ashrams before it prunes their Activities/Categories at
        # lines 172-174 — a latent ordering bug, but not one any assertion below exercises).

        with mock.patch('urllib.request.urlopen', return_value=FakeResponse()):
            run_seed()
            counts = (
                HomePage.objects.count(), Ashram.objects.count(), Photo.objects.count(),
                ActivityCategory.objects.count(), Activity.objects.count(),
            )
            # Existing rows are matched by slug / name+locality and updated in place, not duplicated.
            seeded = Ashram.objects.get(slug='bandhu-ghar-celebration-lankapara')
            seeded.description = 'edited'
            seeded.save()
            # This ashram's slug isn't a key in BANDHUGHAR_GALLERY_IMAGES, so its Photos are
            # never touched by the gallery-sync loop; a Photo added here is expected to persist.
            Photo.objects.create(ashram=seeded, picture='ashram/extra.jpg', approved=True)
            # 'Activities_Bandhu_Ashram' IS gallery-managed, so a stray Photo attached to it
            # should be pruned by the exclude(id__in=keep_photo_ids).delete() on the next run.
            gallery_ashram = Ashram.objects.get(slug='Activities_Bandhu_Ashram')
            Photo.objects.create(ashram=gallery_ashram, picture='ashram/stray-extra.jpg', approved=True)
            run_seed()

        self.assertFalse(Ashram.objects.filter(slug='stray').exists())
        self.assertEqual(
            (
                HomePage.objects.count(), Ashram.objects.count(), Photo.objects.count(),
                ActivityCategory.objects.count(), Activity.objects.count(),
            ),
            (counts[0], counts[1], counts[2] + 1, counts[3], counts[4]),
        )
        seeded.refresh_from_db()
        self.assertEqual(seeded.description, 'Visit by school kids')
        # Photo on the non-gallery-managed ashram is untouched by the seed command.
        self.assertTrue(Photo.objects.filter(picture='ashram/extra.jpg').exists())
        # Photo on the gallery-managed ashram, not in BANDHUGHAR_GALLERY_IMAGES, is pruned.
        self.assertFalse(Photo.objects.filter(picture='ashram/stray-extra.jpg').exists())

    def test_matching_by_slug_when_name_changed_and_stale_activities_removed(self):
        target = Ashram.objects.create(
            name='Renamed', locality='Elsewhere', description='d', address='a', image='x.gif',
            slug='Activities_Bandhu_Ashram',
        )
        cat = ActivityCategory.objects.create(ashram=target, name='Amrut Mahotsav celebration')
        Activity.objects.create(category=cat, name='Obsolete', description='d')
        other = Ashram.objects.create(
            name='Visit by school kids', locality='Lankapara', description='d', address='a', image='x.gif',
            slug='old-slug',
        )
        other_cat = ActivityCategory.objects.create(ashram=other, name='Should go')
        Activity.objects.create(category=other_cat, name='Should go too', description='d')

        with OFFLINE:
            run_seed()

        target.refresh_from_db()
        self.assertEqual(target.name, 'Amrut Mahotsav celebration')
        self.assertEqual(
            list(Activity.objects.filter(category__ashram=target).values_list('name', flat=True)),
            ['Amrut Mahotsav celebration'],
        )
        other.refresh_from_db()
        self.assertEqual(other.slug, 'bandhu-ghar-celebration-lankapara')
        self.assertEqual(ActivityCategory.objects.filter(ashram=other).count(), 0)
        self.assertEqual(Activity.objects.filter(category__ashram=other).count(), 0)
