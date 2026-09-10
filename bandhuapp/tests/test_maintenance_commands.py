"""Maintenance/import commands: offline-safe, idempotent, and never write outside the temp media dir."""

import io
import os
import shutil
import tempfile
import unittest
import urllib.error
import zipfile
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from applications.ankurayan.models import Ankurayan
from applications.patriotism import models as patriotism
from applications.prasantaraktadan import models as raktadan
from applications.sevavrata import models as sevavrata
from bandhuapp import bandhughar_clone_seed, initiative_program_seed
from bandhuapp.management.commands import seed_landing_content, seed_people
from bandhuapp.models import (
    AboutUs,
    CurrentUpdates,
    Designation,
    DesignationRole,
    Gallery,
    PeoplesDesignation,
    Photo,
    Profile,
    RecentActivity,
    SanskarHomePage,
    SanskarHomePhoto,
    Staff,
)
from bandhuapp.tests.support import TINY_GIF, TempMediaMixin, make_profile, make_user


def _offline(*args, **kwargs):
    raise urllib.error.URLError('network disabled in tests')


class FakeResponse:
    """Minimal stand-in for the object `urllib.request.urlopen` returns."""

    def __init__(self, body=b'', status=200):
        self.body = body
        self.status = status

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _url_of(request):
    return request if isinstance(request, str) else request.full_url


def run(command, *args):
    out = io.StringIO()
    call_command(command, *args, stdout=out, stderr=out)
    return out.getvalue()


class OfflineMixin:
    def setUp(self):
        super().setUp()
        patcher = mock.patch('urllib.request.urlopen', side_effect=_offline)
        self.urlopen = patcher.start()
        self.addCleanup(patcher.stop)


class ImportLocalMediaTests(OfflineMixin, TempMediaMixin, TestCase):
    """`import_local_media` resolves every referenced media file from img/, media.zip, or the web."""

    def setUp(self):
        super().setUp()
        # Fake project root so the command's img/ and media.zip lookups never touch the repo.
        self.base_dir = tempfile.mkdtemp(prefix='bandhu-test-base-')
        self.addCleanup(shutil.rmtree, self.base_dir, ignore_errors=True)
        self.img_dir = os.path.join(self.base_dir, 'img')
        os.makedirs(self.img_dir)
        settings_override = override_settings(BASE_DIR=self.base_dir)
        settings_override.enable()
        self.addCleanup(settings_override.disable)
        # seed_landing_content captures MEDIA_ROOT at import; the sub-seeds are covered elsewhere.
        media_patch = mock.patch.object(seed_landing_content, 'MEDIA_ROOT', self.media_dir)
        media_patch.start()
        self.addCleanup(media_patch.stop)
        call_patch = mock.patch('django.core.management.call_command')
        self.call_command = call_patch.start()
        self.addCleanup(call_patch.stop)

    def write_img(self, name, content=TINY_GIF):
        path = os.path.join(self.img_dir, name)
        with open(path, 'wb') as handle:
            handle.write(content)
        return path

    def write_media(self, relative_path, content=TINY_GIF):
        path = os.path.join(self.media_dir, relative_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as handle:
            handle.write(content)
        return path

    def media_exists(self, relative_path):
        return os.path.isfile(os.path.join(self.media_dir, relative_path))

    def test_missing_img_directory_aborts(self):
        shutil.rmtree(self.img_dir)
        output = run('import_local_media')
        self.assertIn('Missing img directory', output)
        self.assertEqual(AboutUs.objects.count(), 0)
        self.call_command.assert_not_called()

    def test_resolves_media_from_every_source(self):
        # TempMediaMixin.media_dir is shared for the whole TestCase class (not reset per
        # test), so an earlier test's leftover gallery files would otherwise pollute the
        # "synced N gallery photo(s)" count here. Start this test from a clean media dir.
        shutil.rmtree(self.media_dir, ignore_errors=True)
        os.makedirs(self.media_dir)
        self.write_img('our_mission.jpg')          # explicit source
        self.write_img('pimg1.jpg', b'alias')      # alias for ankurayan.jpg
        self.write_img('man.png')                  # basename match
        os.makedirs(os.path.join(self.img_dir, 'subdir'))  # directories are ignored by the index
        with zipfile.ZipFile(os.path.join(self.base_dir, 'media.zip'), 'w') as archive:
            archive.writestr('media/bandhuapp/gallery/zipped.jpg', b'zip-bytes')
            archive.writestr('bandhuapp/gallery/Upper.jpg', b'upper')
        self.write_media('bandhuapp/gallery/present.jpg')

        Photo.objects.create(picture='bandhuapp/gallery/zipped.jpg', approved=False)
        Photo.objects.create(picture='bandhuapp/gallery/UPPER.JPG', approved=False)
        Photo.objects.create(picture='bandhuapp/gallery/present.jpg', approved=False)
        Photo.objects.create(picture='main_page/initiatives/old.jpg')
        Photo.objects.create(picture='bandhuapp/gallery/stale.jpg')
        make_profile(make_user('a@example.com'), profile_pic='profile_photos/ankurayan.jpg')
        make_profile(make_user('b@example.com'), profile_pic='remote/web.jpg')
        make_profile(make_user('c@example.com'), profile_pic='remote/bad.jpg')
        make_profile(make_user('d@example.com'), profile_pic='remote/gone.jpg')

        def fake_urlopen(request, timeout=None):
            url = _url_of(request)
            if url.endswith('/web.jpg'):
                return FakeResponse(b'downloaded')
            if url.endswith('/bad.jpg'):
                return FakeResponse(b'', status=404)
            raise urllib.error.URLError('offline')

        self.urlopen.side_effect = fake_urlopen
        output = run('import_local_media')

        self.assertIn('Extracted zipped.jpg from media.zip', output)
        self.assertIn('Copied our_mission.jpg -> bandhuapp/banner/our_mission.jpg', output)
        self.assertIn('Copied pimg1.jpg -> profile_photos/ankurayan.jpg', output)
        self.assertIn('Downloaded web.jpg -> remote/web.jpg', output)
        self.assertIn('No local source for remote/bad.jpg', output)
        self.assertIn('No local source for remote/gone.jpg', output)
        self.assertIn('No local source for profile_photos/woman.png', output)
        for path in (
            'bandhuapp/gallery/zipped.jpg', 'bandhuapp/gallery/UPPER.JPG', 'bandhuapp/banner/our_mission.jpg',
            'bandhuapp/sanskar/our_mission.jpg', 'profile_photos/ankurayan.jpg', 'profile_photos/man.png',
            'remote/web.jpg',
        ):
            self.assertTrue(self.media_exists(path), path)
        with open(os.path.join(self.media_dir, 'profile_photos/ankurayan.jpg'), 'rb') as handle:
            self.assertEqual(handle.read(), b'alias')
        with open(os.path.join(self.media_dir, 'remote/web.jpg'), 'rb') as handle:
            self.assertEqual(handle.read(), b'downloaded')
        self.assertFalse(self.media_exists('remote/bad.jpg'))
        self.assertFalse(self.media_exists('remote/gone.jpg'))
        # Nothing was written to the fake project root or the real media dir.
        self.assertEqual(sorted(os.listdir(self.base_dir)), ['img', 'media.zip'])

        # Gallery sync: legacy initiative photos and stale rows are gone, real files approved.
        self.assertFalse(Photo.objects.filter(picture__startswith='main_page/').exists())
        self.assertFalse(Photo.objects.filter(picture='bandhuapp/gallery/stale.jpg').exists())
        self.assertTrue(Photo.objects.get(picture='bandhuapp/gallery/present.jpg').approved)
        self.assertEqual(AboutUs.objects.count(), 1)
        self.assertEqual(Gallery.objects.count(), 1)
        self.assertIn('synced 3 gallery photo(s)', output)
        # zip_copied is 2: zipped.jpg (exact match) and UPPER.JPG (case-insensitive match
        # against the zip's "Upper.jpg" entry) are both extracted from media.zip.
        self.assertIn('(2 from media.zip, 1 from production)', output)
        seeds = [call.args[0] for call in self.call_command.call_args_list]
        self.assertEqual(seeds[:2], ['seed_landing_content', 'seed_landing_notices'])
        self.assertEqual(len(seeds), 8)

    def test_gallery_sync_dedupes_tags_and_keeps_captions(self):
        gallery = 'bandhuapp/gallery'
        self.write_media(f'{gallery}/kids.jpg', b'same')
        self.write_media(f'{gallery}/kids_AbC1234.jpg', b'same')     # duplicate suffix -> collapsed
        self.write_media(f'{gallery}/ankurayan_day.jpg', b'a')
        self.write_media(f'{gallery}/kendra_class.jpg', b'b')
        self.write_media(f'{gallery}/bandhughar_camp.jpg', b'c')
        self.write_media(f'{gallery}/meeting_2019.jpg', b'd')
        self.write_media(f'{gallery}/about-slide-1.png', b'e')       # skipped: about slide
        self.write_media(f'{gallery}/pimg1.jpg', b'f')                # skipped: placeholder
        self.write_media(f'{gallery}/notes.txt', b'g')                # skipped: not an image
        self.write_media(f'{gallery}/site-logo.png', b'h')            # skipped: logo
        os.makedirs(os.path.join(self.media_dir, gallery, 'nested'))  # skipped: directory
        Photo.objects.create(picture=f'{gallery}/kids.jpg', caption='Keep me')

        output = run('import_local_media')
        self.assertIn('synced 5 gallery photo(s)', output)
        photos = {photo.picture.name: photo for photo in Photo.objects.all()}
        self.assertEqual(
            sorted(photos),
            sorted([
                f'{gallery}/kids.jpg', f'{gallery}/ankurayan_day.jpg', f'{gallery}/kendra_class.jpg',
                f'{gallery}/bandhughar_camp.jpg', f'{gallery}/meeting_2019.jpg',
            ]),
        )
        self.assertEqual(photos[f'{gallery}/kids.jpg'].caption, 'Keep me')
        self.assertEqual(photos[f'{gallery}/kids.jpg'].tags, 'other')
        self.assertEqual(photos[f'{gallery}/ankurayan_day.jpg'].tags, 'ankurayan')
        self.assertEqual(photos[f'{gallery}/ankurayan_day.jpg'].caption, 'ankurayan day')
        self.assertEqual(photos[f'{gallery}/kendra_class.jpg'].tags, 'anandakendra')
        self.assertEqual(photos[f'{gallery}/bandhughar_camp.jpg'].tags, 'bandhughar')
        self.assertEqual(photos[f'{gallery}/meeting_2019.jpg'].tags, 'activities')
        self.assertTrue(all(photo.approved for photo in photos.values()))

    def test_rerun_updates_existing_site_copy(self):
        AboutUs.objects.create(tagline='old', desc='old')
        Gallery.objects.create(tagline='old')
        run('import_local_media')
        run('import_local_media')
        self.assertEqual(AboutUs.objects.count(), 1)
        self.assertEqual(Gallery.objects.count(), 1)
        self.assertNotEqual(AboutUs.objects.get().tagline, 'old')
        self.assertNotEqual(Gallery.objects.get().tagline, 'old')

    def test_relative_media_root_is_anchored_at_base_dir(self):
        self.write_img('man.png')
        with override_settings(MEDIA_ROOT='rel-media'):
            run('import_local_media')
        self.assertTrue(os.path.isfile(os.path.join(self.base_dir, 'rel-media', 'profile_photos', 'man.png')))


class SeedPeopleTests(OfflineMixin, TempMediaMixin, TestCase):
    """`seed_people` builds the People page and enriches it from the live site when reachable."""

    EXPECTED_STAFF = len(seed_people.DEFAULT_PEOPLE_WITH_WEBTEAM)

    def setUp(self):
        super().setUp()
        # media_dir is shared for the whole TestCase class (TempMediaMixin resets it only
        # between classes), so a downloaded/placeholder photo left by one test would make
        # `_download_profile_photo`/`_ensure_placeholder` short-circuit for another. Start
        # each test from a clean profile_photos/ directory.
        shutil.rmtree(os.path.join(self.media_dir, 'profile_photos'), ignore_errors=True)

    def photo_path(self, name):
        return os.path.join(self.media_dir, 'profile_photos', name)

    # Regression: DesignationRole.save() proper-cases `title` on every save, while
    # seed_people's DEFAULT_OFFICE_BEARER_ROLES holds a mixed-case title ("...Outreach and
    # Website)"). A second run's `get_or_create` used to search for the raw mixed-case
    # string, miss the stored Title-Case row, insert a duplicate, and trip the
    # (designation, title) unique constraint -> IntegrityError. seed_people now looks the
    # role up via proper_case(), so a second run is a no-op instead of a crash.
    def test_offline_seed_uses_placeholders_and_is_idempotent(self):
        output = run('seed_people')
        self.assertEqual(Designation.objects.count(), 3)
        self.assertEqual(DesignationRole.objects.count(), 5)
        self.assertEqual(Staff.objects.count(), self.EXPECTED_STAFF)
        self.assertEqual(PeoplesDesignation.objects.count(), self.EXPECTED_STAFF)
        self.assertIn(f'{self.EXPECTED_STAFF} staff member(s)', output)
        self.assertIn(f'synced {self.EXPECTED_STAFF} profile photo(s)', output)
        self.assertIn('applied 0 live update(s)', output)

        president = PeoplesDesignation.objects.get(role__title='President')
        self.assertEqual(president.staff.profile.first_name, 'Binod')
        self.assertEqual(Profile.objects.get(first_name='Richa').profile_pic.name, 'profile_photos/woman.png')
        self.assertEqual(Profile.objects.get(first_name='Sanjeeb').profile_pic.name, 'profile_photos/man.png')
        self.assertTrue(os.path.isfile(self.photo_path('man.png')))
        self.assertTrue(os.path.isfile(self.photo_path('woman.png')))

        counts = (Designation.objects.count(), DesignationRole.objects.count(), Staff.objects.count(),
                  PeoplesDesignation.objects.count(), Profile.objects.count())
        output = run('seed_people')
        self.assertEqual(
            counts,
            (Designation.objects.count(), DesignationRole.objects.count(), Staff.objects.count(),
             PeoplesDesignation.objects.count(), Profile.objects.count()),
        )
        self.assertIn('synced 0 profile photo(s)', output)

    def test_existing_rows_are_refreshed_not_duplicated(self):
        Designation.objects.create(title='Core Team', rank=42)
        user = make_user(seed_people._email_for_person('Sanjeeb', 'Mohapatra'))
        make_profile(user, first_name='Wrong', last_name='Name', profession='Old', profile_pic='profile_photos/custom.jpg')
        os.makedirs(self.photo_path(''), exist_ok=True)
        with open(self.photo_path('custom.jpg'), 'wb') as handle:
            handle.write(TINY_GIF)

        run('seed_people')
        self.assertEqual(Designation.objects.get(title='Core Team').rank, 1)
        profile = Profile.objects.get(user=user)
        self.assertEqual((profile.first_name, profile.last_name), ('Sanjeeb', 'Mohapatra'))
        self.assertEqual(profile.profession, 'Senior Solution Data Architect')
        # A picture that already exists on disk is left alone.
        self.assertEqual(profile.profile_pic.name, 'profile_photos/custom.jpg')
        self.assertEqual(Staff.objects.filter(profile=profile).count(), 1)

    def test_live_site_data_updates_profiles_and_photos(self):
        html = '''
        <div class="card">
          <img src="/media/profile_photos/sanjeeb-live.jpg" class="rounded-circle">
          <h5 class="my-2">Sanjeeb   Mohapatra</h5>
          <p class="text-muted mb-1">Live Architect</p>
          <p class="text-muted mb-4">Core Team</p>
        </div>
        <div class="card">
          <img src="/media/profile_photos/sanjeeb-live.jpg">
          <h5 class="my-2">Sanjeeb Mohapatra</h5>
          <p class="text-muted mb-1">Duplicate card</p>
          <p class="text-muted mb-4">Core Team</p>
        </div>
        <div class="card">
          <img src="/media/profile_photos/x.jpg">
          <h5 class="my-2">Sanjeeb Mohapatra</h5>
          <p class="text-muted mb-1"></p>
          <p class="text-muted mb-4">Web Team</p>
        </div>
        <div class="card">
          <img src="/media/profile_photos/x.jpg">
          <h5 class="my-2">Ghost Person</h5>
          <p class="text-muted mb-1">Nobody</p>
          <p class="text-muted mb-4">Core Team</p>
        </div>
        <div class="card">
          <img src="/media/profile_photos/x.jpg">
          <h5 class="my-2">Mononym</h5>
          <p class="text-muted mb-1">Single name</p>
          <p class="text-muted mb-4">Core Team</p>
        </div>
        <div class="card">
          <img src="/media/profile_photos/x.jpg">
          <h5 class="my-2">Binod Kumar Sahoo</h5>
          <p class="text-muted mb-1">Academic administrator</p>
          <p class="text-muted mb-4">Unknown Group</p>
        </div>
        '''

        def fake_urlopen(request, timeout=None):
            url = _url_of(request)
            if url == seed_people.LIVE_PEOPLE_URL:
                return FakeResponse(html.encode('utf-8'))
            if url.endswith('/Biswa.png'):
                raise urllib.error.URLError('missing on server')
            return FakeResponse(b'photo-bytes')

        self.urlopen.side_effect = fake_urlopen
        output = run('seed_people')

        sanjeeb = Profile.objects.get(first_name='Sanjeeb')
        self.assertEqual(sanjeeb.profession, 'Live Architect')
        # Cards are applied in document order with no per-field priority: the later "Web Team"
        # card (photo x.jpg) overwrites the photo set by the earlier "Core Team" card
        # (sanjeeb-live.jpg), even though its own profession field is blank.
        self.assertEqual(sanjeeb.profile_pic.name, 'profile_photos/x.jpg')
        self.assertIn('Updated live profile data for Sanjeeb Mohapatra', output)
        # The extra Web Team card created a second designation for him; the rest were ignored.
        self.assertEqual(PeoplesDesignation.objects.filter(staff__profile=sanjeeb).count(), 2)
        # 3 = the Core Team card's field change, plus the Web Team card's field change and its
        # newly-created PeoplesDesignation row.
        self.assertIn('applied 3 live update(s)', output)
        self.assertEqual(Profile.objects.get(first_name='Binod').profession, 'Academic Administrator')
        # Mapped live photos were downloaded; the one that failed fell back to the placeholder.
        self.assertEqual(Profile.objects.get(first_name='Rajendra').profile_pic.name, 'profile_photos/image.png')
        self.assertTrue(os.path.isfile(self.photo_path('image.png')))
        self.assertEqual(Profile.objects.get(first_name='Ranjan').profile_pic.name, 'profile_photos/man.png')
        self.assertFalse(os.path.isfile(self.photo_path('Biswa.png')))

        # Second run: downloads are cached on disk, so no photo is re-fetched. Live updates
        # do NOT settle at 0, though: Sanjeeb has two live cards ("Core Team" wants photo
        # sanjeeb-live.jpg, "Web Team" wants x.jpg) and the applier has no per-field priority,
        # so each run both cards see a photo that is not theirs and rewrite it. The pair
        # oscillates forever, costing 2 writes per run. Pinned here deliberately: if the
        # applier ever gains priority rules this drops to 0 and the test should be updated.
        output = run('seed_people')
        self.assertIn('synced 0 profile photo(s)', output)
        self.assertIn('applied 2 live update(s)', output)
        self.assertEqual(PeoplesDesignation.objects.filter(staff__profile=sanjeeb).count(), 2)
        self.assertEqual(Profile.objects.get(first_name='Sanjeeb').profession, 'Live Architect')

    def test_resolve_profile_photo_redownloads_named_picture(self):
        profile = make_profile(make_user(), first_name='Some', last_name='One', profile_pic='profile_photos/old.jpg')
        self.urlopen.side_effect = lambda request, timeout=None: FakeResponse(b'bytes')
        self.assertEqual(seed_people._resolve_profile_photo(self.media_dir, profile), 'profile_photos/old.jpg')
        self.assertTrue(os.path.isfile(self.photo_path('old.jpg')))

    def test_resolve_profile_photo_without_any_source(self):
        profile = make_profile(make_user(), first_name='Some', last_name='One')
        with override_settings(BASE_DIR=self.media_dir):  # no img/ folder -> no placeholder
            self.assertEqual(seed_people._resolve_profile_photo(self.media_dir, profile), '')

    def test_fetch_live_people_cards_offline_returns_nothing(self):
        self.assertEqual(seed_people._fetch_live_people_cards(), [])
        self.assertEqual(seed_people._apply_live_people_cards([], {}), 0)


class FixProfileCasingTests(TestCase):
    def test_reformats_only_rows_that_need_it(self):
        profile = make_profile(make_user(), street_address2='flat 2')
        Profile.objects.filter(pk=profile.pk).update(
            first_name='jOHN', last_name='doe', city='cuttack', street_address2='',
        )
        clean = make_profile(make_user('clean@example.com'))
        group = Designation.objects.create(title='Office Bearers', rank=1)
        Designation.objects.filter(pk=group.pk).update(title='office bearers')
        role = DesignationRole.objects.create(designation=group, title='President', rank=1)
        DesignationRole.objects.filter(pk=role.pk).update(title='PRESIDENT')
        staff = Staff.objects.create(profile=profile, about='x')
        note = PeoplesDesignation.objects.create(staff=staff, designation=group, desc='retired teacher ')
        PeoplesDesignation.objects.create(staff=Staff.objects.create(profile=clean, about='y'), designation=group)

        # PeoplesDesignation.save() already applies proper_case to `desc` on create, so
        # `note.desc` is already 'Retired Teacher' before the command runs; 0 notes change.
        self.assertEqual(PeoplesDesignation.objects.get(pk=note.pk).desc, 'Retired Teacher')

        output = run('fix_profile_casing')
        self.assertIn('Updated 1 profile(s), 0 designation note(s), 1 group(s), and 1 role(s).', output)
        profile.refresh_from_db()
        self.assertEqual((profile.first_name, profile.last_name, profile.city), ('John', 'Doe', 'Cuttack'))
        self.assertEqual(profile.street_address2, '')
        self.assertEqual(Designation.objects.get(pk=group.pk).title, 'Office Bearers')
        self.assertEqual(DesignationRole.objects.get(pk=role.pk).title, 'President')
        self.assertEqual(PeoplesDesignation.objects.get(pk=note.pk).desc, 'Retired Teacher')

        output = run('fix_profile_casing')
        self.assertIn('Updated 0 profile(s), 0 designation note(s), 0 group(s), and 0 role(s).', output)


class FixNoticeLinksTests(TestCase):
    def test_rewrites_legacy_links(self):
        Ankurayan.objects.create(
            year=2019, title='Ankurayan 2019', theme='t', description='d',
            start_date='2019-12-10', end_date='2019-12-12', slug='ankurayan-2019',
        )
        detail = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': 'ankurayan-2019'})
        with_year = CurrentUpdates.objects.create(desc='Ankurayan 2019 report', url='https://bandhuodisha.in/ankurayan/')
        no_year = CurrentUpdates.objects.create(desc='Ankurayan photos', url='http://www.bandhuodisha.in/ankurayan')
        charity = CurrentUpdates.objects.create(desc='Charity', url='https://bandhuodisha.in/other_activities/')
        untouched = CurrentUpdates.objects.create(desc='Local', url='/people/')
        empty = CurrentUpdates.objects.create(desc='Empty', url='#')
        recent = RecentActivity.objects.create(
            title='Ankurayan 2019', description='festival', link='https://bandhuodisha.in/ankurayan/',
        )
        external = RecentActivity.objects.create(title='News', description='x', link='https://example.com/a')
        blank = RecentActivity.objects.create(title='Blank', description='x')

        output = run('fix_notice_links')
        self.assertIn('Updated 3 current update(s), 1 recent activit(ies).', output)
        self.assertEqual(CurrentUpdates.objects.get(pk=with_year.pk).url, detail)
        self.assertEqual(CurrentUpdates.objects.get(pk=no_year.pk).url, reverse('ankurayan:ankurayan'))
        self.assertEqual(CurrentUpdates.objects.get(pk=charity.pk).url, reverse('charitywork:charity_work'))
        self.assertEqual(CurrentUpdates.objects.get(pk=untouched.pk).url, '/people/')
        self.assertEqual(CurrentUpdates.objects.get(pk=empty.pk).url, '#')
        self.assertEqual(RecentActivity.objects.get(pk=recent.pk).link, detail)
        self.assertEqual(RecentActivity.objects.get(pk=external.pk).link, 'https://example.com/a')
        self.assertEqual(RecentActivity.objects.get(pk=blank.pk).link, '#')

        output = run('fix_notice_links')
        self.assertIn('Updated 0 current update(s), 0 recent activit(ies).', output)


class InitiativeProgramSeedTests(OfflineMixin, TempMediaMixin, TestCase):
    PROGRAMS = (raktadan, patriotism, sevavrata)

    def home_image(self, prefix):
        return os.path.join(self.media_dir, prefix, 'index', 'home.jpg')

    def test_seed_all_programs_is_idempotent(self):
        output = run('seed_initiative_programs_from_bandhughar')
        for models in self.PROGRAMS:
            label = models.HomePage._meta.app_label
            with self.subTest(program=label):
                page = models.HomePage.objects.get()
                self.assertEqual(page.pk, 1)
                self.assertEqual(page.picture.name, f'{label}/index/home.jpg')
                self.assertTrue(page.image_caption_en)
                self.assertTrue(os.path.isfile(self.home_image(label)))
        self.assertIn('Prasanta Raktadan Shibir: homepage seeded, 0 year entr(y/ies)', output)
        self.assertIn('Odisha Satabdi Sevavrata: homepage seeded', output)

        run('seed_initiative_programs_from_bandhughar')
        for models in self.PROGRAMS:
            self.assertEqual(models.HomePage.objects.count(), 1)

    def test_clear_flag_removes_year_data_but_keeps_homepage(self):
        patriotism.Ashram.objects.create(
            name='Old', locality='Cuttack', description='d', address='a', image='t/h.gif', slug='old',
        )
        patriotism.HomePage.objects.create(pk=1, tagline='custom', description='custom', picture='x/y.jpg')
        output = run('seed_initiative_programs_from_bandhughar', '--clear')
        self.assertIn('Cleared imported content for Patriotism in Action.', output)
        self.assertEqual(patriotism.Ashram.objects.count(), 0)
        page = patriotism.HomePage.objects.get()
        self.assertEqual(page.tagline, 'Patriotism in Action')
        self.assertEqual(page.picture.name, 'patriotism/index/home.jpg')

    def test_missing_fallback_image_is_reported(self):
        # media_dir is shared for the whole TestCase class; an earlier test may already have
        # placed sevavrata/index/home.jpg there, which would short-circuit the fallback-image
        # copy this test is checking. Start from a clean slate for this path.
        if os.path.isfile(self.home_image('sevavrata')):
            os.remove(self.home_image('sevavrata'))
        out = io.StringIO()
        with override_settings(BASE_DIR=self.media_dir):  # no static/img or img/ under here
            result = initiative_program_seed.seed_initiative_homepage(
                media_prefix='sevavrata', program_key='sevavrata',
                homepage_model=sevavrata.HomePage, stdout=out,
            )
        self.assertIn('Warning: no fallback image for sevavrata/index/home.jpg', out.getvalue())
        self.assertEqual(result, {'program_label': 'Odisha Satabdi Sevavrata', 'program_count': 0})
        self.assertEqual(sevavrata.HomePage.objects.get().picture.name, 'sevavrata/index/home.jpg')
        self.assertFalse(os.path.isfile(self.home_image('sevavrata')))

    def test_clear_without_models_is_a_noop(self):
        raktadan.Ashram.objects.create(
            name='Keep', locality='Cuttack', description='d', address='a', image='t/h.gif', slug='keep',
        )
        initiative_program_seed.seed_initiative_homepage(
            media_prefix='prasantaraktadan', program_key='prasantaraktadan',
            homepage_model=raktadan.HomePage, clear_content=True,
        )
        self.assertEqual(raktadan.Ashram.objects.count(), 1)

    def test_bandhughar_clone_compat_entry_point(self):
        raktadan.Ashram.objects.create(
            name='One', locality='Cuttack', description='d', address='a', image='t/h.gif', slug='one',
        )
        result = bandhughar_clone_seed.seed_bandhughar_clone(
            media_prefix='prasantaraktadan', program_label='Custom Label', download_referer='x',
            homepage_model=raktadan.HomePage, ashram_model=raktadan.Ashram,
        )
        self.assertEqual(result, {
            'program_count': 1, 'gallery_total': 0, 'activity_total': 0, 'program_label': 'Custom Label',
        })
        result = bandhughar_clone_seed.seed_bandhughar_clone(
            media_prefix='prasantaraktadan', program_label='', download_referer='x',
            homepage_model=raktadan.HomePage,
        )
        self.assertEqual(result['program_label'], 'Prasanta Raktadan Shibir')
        self.assertEqual(result['program_count'], 0)
        with self.assertRaises(ValueError):
            bandhughar_clone_seed.seed_bandhughar_clone(
                media_prefix='unknown', program_label='', download_referer='x', homepage_model=raktadan.HomePage,
            )


class SeedSanskarContentTests(OfflineMixin, TempMediaMixin, TestCase):
    """Remaining branches of `seed_sanskar_content`: remote download, gallery reorder, stale removal."""

    def media(self, relative_path):
        return os.path.join(self.media_dir, relative_path)

    def test_downloads_missing_images_when_online(self):
        self.urlopen.side_effect = lambda request, timeout=None: FakeResponse(b'remote-bytes')
        with override_settings(BASE_DIR=self.media_dir):  # no bundled img/ -> every image comes from the web
            output = run('seed_sanskar_content')
        self.assertIn('4 gallery photo(s)', output)
        self.assertNotIn('Missing source image', output)
        self.assertTrue(os.path.isfile(self.media('bandhuapp/sanskar/collage_1.jpg')))
        self.assertTrue(os.path.isfile(self.media('bandhuapp/sanskar/pimg6.jpg')))
        page = SanskarHomePage.objects.get()
        self.assertEqual(page.hero_image.name, 'bandhuapp/sanskar/collage_1.jpg')
        self.assertEqual(SanskarHomePhoto.objects.filter(page=page).count(), 4)

    def test_offline_without_sources_warns_and_seeds_copy_only(self):
        # media_dir is shared for the whole TestCase class; an earlier test may already have
        # copied these images into bandhuapp/sanskar/, which would short-circuit the "missing
        # source" warning this test is checking. Start from a clean slate for that directory.
        shutil.rmtree(self.media('bandhuapp/sanskar'), ignore_errors=True)
        with override_settings(BASE_DIR=self.media_dir):
            output = run('seed_sanskar_content')
        self.assertIn('Missing source image: collage_1.jpg', output)
        self.assertIn('0 gallery photo(s)', output)
        page = SanskarHomePage.objects.get()
        self.assertFalse(page.hero_image)
        self.assertEqual(SanskarHomePhoto.objects.count(), 0)

    def test_gallery_reorders_existing_and_drops_stale_photos(self):
        # media_dir is shared for the whole TestCase class; clear any images an earlier test
        # left under bandhuapp/sanskar/ so only collage.jpg and pimg2.jpg (written below) are
        # available sources here.
        shutil.rmtree(self.media('bandhuapp/sanskar'), ignore_errors=True)
        page = SanskarHomePage.objects.create(tagline='old', description='old')
        for relative_path, _source in (('bandhuapp/sanskar/collage.jpg', ''), ('bandhuapp/sanskar/pimg2.jpg', '')):
            os.makedirs(os.path.dirname(self.media(relative_path)), exist_ok=True)
            with open(self.media(relative_path), 'wb') as handle:
                handle.write(TINY_GIF)
        kept = SanskarHomePhoto.objects.create(page=page, picture='bandhuapp/sanskar/collage.jpg', sort_order=9)
        stale = SanskarHomePhoto.objects.create(page=page, picture='bandhuapp/sanskar/stale.jpg', sort_order=0)
        blank = SanskarHomePhoto.objects.create(page=page, picture='', sort_order=1)

        with override_settings(BASE_DIR=self.media_dir):
            run('seed_sanskar_content')
        kept.refresh_from_db()
        self.assertEqual(kept.sort_order, 0)
        self.assertFalse(SanskarHomePhoto.objects.filter(pk__in=[stale.pk, blank.pk]).exists())
        self.assertEqual(SanskarHomePhoto.objects.filter(page=page).count(), 2)
        page.refresh_from_db()
        self.assertEqual(page.tagline, 'Anandakendra and Ankurayan')
