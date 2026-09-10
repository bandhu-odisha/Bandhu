"""Regression tests for the Ankurayan management commands (no network)."""

import io
import os
import shutil
import tempfile
import urllib.error
from datetime import date
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings

from bandhuapp.tests.support import TINY_GIF, TempMediaMixin
from applications.ankurayan.guest_examples import EXAMPLE_GUESTS
from applications.ankurayan.management.commands import seed_ankurayan_content as seed
from applications.ankurayan.models import Ankurayan, Guest, HomePage, Photo

OFFLINE = mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline'))


def make_ankurayan(year, **overrides):
    data = dict(
        year=year, title=f'Ankurayan {year}', theme='T', description='D',
        start_date=date(year, 12, 17), end_date=date(year, 12, 19),
        logo='ankurayan/logo/custom.jpg', slug=str(year),
    )
    data.update(overrides)
    return Ankurayan.objects.create(**data)


def run(name, *args, **kwargs):
    out = io.StringIO()
    call_command(name, *args, stdout=out, **kwargs)
    return out.getvalue()


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


PRODUCTION_HTML = """
<div id="modalDescription"><div id="viewDescription">Live description</div></div>
<div class="ankurayan-visitors-intro extra">Live visitors</div>
<div class="ankurayan-publications-intro">Live publications</div>
<h6 class="guest-card-name">Live Guest</h6><p class="guest-card-profession">Judge</p>
<p class="guest-quote-preview">"It was &#39;great&#39; &quot;fun&quot;…</p>
<h6 class="guest-card-name">Quiet Guest</h6><p class="guest-card-profession">Official</p>
<p class="ankurayan-detail-schedule-dates">Starts on <strong>17 Dec, 2024</strong>
Ends on <strong>19 December, 2024</strong></p>
<script>var djangoAlbumImages = [{src: '/media/ankurayan/2024/one.jpg?v=1'}, {src: '/media/ankurayan/logo/x.jpg'}];</script>
<img class="ankurayan-sidebar-gallery__img" src="/media/ankurayan/2024/two.png">
"""


class SeedHelperTests(TestCase):
    def test_parse_display_date(self):
        self.assertEqual(seed._parse_display_date(' 17 Dec, 2024 '), date(2024, 12, 17))
        self.assertEqual(seed._parse_display_date('19 December, 2024'), date(2024, 12, 19))
        self.assertIsNone(seed._parse_display_date('nonsense'))

    def test_extract_schedule_dates_falls_back(self):
        self.assertEqual(seed._extract_schedule_dates('<p>no dates</p>', 2021),
                         seed.YEAR_SCHEDULE[2021])
        self.assertEqual(seed._extract_schedule_dates('', 1999),
                         (date(1999, 12, 17), date(1999, 12, 19)))
        html = 'Starts on <strong>1 Jan, 2020</strong> Ends on <strong>bad</strong>'
        self.assertEqual(seed._extract_schedule_dates(html, 2020), seed.YEAR_SCHEDULE[2020])

    def test_normalize_media_path(self):
        self.assertEqual(seed._normalize_media_path('https://x/media/ankurayan/2024/a.jpg?v=2'),
                         'ankurayan/2024/a.jpg')
        self.assertEqual(seed._normalize_media_path('/img/a.jpg'), 'img/a.jpg')

    def test_prefer_clean_filenames(self):
        paths = ['ankurayan/2024/photo_AbC1234.jpg', 'ankurayan/2024/photo.jpg',
                 'ankurayan/2024/other_XyZ9876.jpg', 'ankurayan/2024/Other.JPG']
        self.assertEqual(seed._prefer_clean_filenames(paths),
                         ['ankurayan/2024/Other.JPG', 'ankurayan/2024/photo.jpg'])
        # DJANGO_DUP_SUFFIX only matches a genuine Django-style random suffix (exactly
        # 7 alnum chars), so a plain numeric suffix like "_1"/"_2" isn't recognized as a
        # duplicate marker and both paths are kept as distinct files.
        self.assertEqual(
            seed._prefer_clean_filenames(['a/b_1.jpg', 'a/b_2.jpg']),
            ['a/b_1.jpg', 'a/b_2.jpg'],
        )
        # A genuine 7-char random suffix collapses onto the clean filename.
        self.assertEqual(
            seed._prefer_clean_filenames(['a/b.jpg', 'a/b_AbC1234.jpg']),
            ['a/b.jpg'],
        )

    def test_extract_gallery_paths(self):
        paths = seed._extract_gallery_paths(PRODUCTION_HTML)
        self.assertEqual(paths, ['ankurayan/2024/one.jpg', 'ankurayan/2024/two.png'])
        raw = 'x "/media/ankurayan/2020/raw.jpg" "/media/ankurayan/2020/raw.jpg"'
        self.assertEqual(seed._extract_gallery_paths(raw), ['ankurayan/2020/raw.jpg'])
        self.assertEqual(seed._extract_gallery_paths('nothing'), [])

    def test_extract_production_fields(self):
        fields = seed._extract_production_fields(PRODUCTION_HTML, 2024)
        self.assertEqual(fields['description'], 'Live description')
        self.assertEqual(fields['visitors'], 'Live visitors')
        self.assertEqual(fields['publications'], 'Live publications')
        self.assertEqual(fields['start_date'], date(2024, 12, 17))
        self.assertEqual(fields['end_date'], date(2024, 12, 19))
        self.assertEqual(fields['guests'][0], {
            'name': 'Live Guest', 'profession': 'Judge', 'quote': 'It was \'great\' "fun"...'})
        self.assertEqual(fields['guests'][1]['name'], 'Quiet Guest')

    def test_extract_production_fields_fallbacks(self):
        fields = seed._extract_production_fields('<html></html>', 2018)
        self.assertEqual(fields['description'], seed.YEAR_THEMES_DICT[2018])
        self.assertEqual(fields['visitors'], seed.FALLBACK_VISITORS)
        self.assertIn('Ankurayan 2018', fields['publications'])
        self.assertEqual(fields['guests'], [])
        self.assertEqual(seed._extract_production_fields('', 1999)['description'],
                         'Theme of Ankurayan 1999')


class SeedAnkurayanContentTests(TempMediaMixin, TestCase):
    def test_offline_seed_is_idempotent(self):
        # TempMediaMixin's media_dir is shared for the whole test class (setUpClass), and
        # sibling tests write real gallery image files into ankurayan/2011/ and
        # ankurayan/2020/ under it. Use a private, empty MEDIA_ROOT so "no gallery files
        # available offline" doesn't depend on alphabetical test execution order.
        empty_media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-empty-')
        self.addCleanup(shutil.rmtree, empty_media_dir, True)
        with OFFLINE as urlopen, override_settings(MEDIA_ROOT=empty_media_dir):
            out = run('seed_ankurayan_content', '--offline')
            # --offline only skips the production-HTML fetch and the logo pre-fetch loop;
            # gallery images not found locally still go through _ensure_media_file's
            # urlopen fallback (and fail offline, producing the "Missing gallery file"
            # warning asserted below).
            self.assertTrue(urlopen.called)
            first = (Ankurayan.objects.count(), Guest.objects.count(), Photo.objects.count())
            run('seed_ankurayan_content', '--offline')
        self.assertEqual(first, (Ankurayan.objects.count(), Guest.objects.count(), Photo.objects.count()))
        self.assertEqual(Ankurayan.objects.count(), len(seed.YEAR_THEMES))
        self.assertEqual(Guest.objects.count(), len(seed.YEAR_THEMES) * (len(EXAMPLE_GUESTS) + len(seed.EXTRA_GUESTS)))
        self.assertEqual(Photo.objects.count(), 0)
        self.assertIn('Missing gallery file: ankurayan/2020/punchi.jpg', out)
        self.assertIn('synced 0 year page(s)', out)

        home = HomePage.objects.get(pk=1)
        self.assertEqual(home.tagline, 'Ankurayan')
        self.assertEqual(home.picture.name, 'ankurayan/index/Ankurayan_2025_Logo.png')
        self.assertTrue(home.image_caption_en)

        a2018 = Ankurayan.objects.get(year=2018)
        self.assertEqual(a2018.slug, '2018')
        self.assertEqual(a2018.theme, seed.YEAR_THEMES_DICT[2018])
        self.assertEqual((a2018.start_date, a2018.end_date), seed.YEAR_SCHEDULE[2018])
        # NOTE (app quirk, not fixed here per task scope): no logo file is ever written for
        # 2018 (see the isolated MEDIA_ROOT above), but get_or_create's `defaults` already
        # sets logo='ankurayan/logo/logo-2018.jpg' at creation time, and the "fall back to
        # the default logo" check (seed_ankurayan_content.py ~L431) only fires when the
        # *existing* logo is falsy or literally ends with 'Logo.jpg' — 'logo-2018.jpg'
        # doesn't, so the row ends up pointing at a logo file that was never downloaded.
        self.assertEqual(a2018.logo.name, 'ankurayan/logo/logo-2018.jpg')
        self.assertEqual(a2018.visitors, seed.FALLBACK_VISITORS)
        self.assertIn('Ankurayan 2018', a2018.publications)
        self.assertTrue(os.path.isdir(os.path.join(self.media_dir, 'ankurayan', 'logo')))

    def test_offline_seed_preserves_custom_logo_and_removes_stale_years(self):
        kept = make_ankurayan(2024, logo='ankurayan/logo/custom.jpg', slug='old-slug')
        default_logo = make_ankurayan(2020, logo='ankurayan/logo/Logo.jpg')
        stale = make_ankurayan(1999)
        Guest.objects.create(ankurayan=kept, name=EXAMPLE_GUESTS[0]['name'], profession='x')
        Photo.objects.create(ankurayan=kept, picture='ankurayan/2024/stale.jpg', approved=True)
        (os.makedirs(os.path.join(self.media_dir, 'ankurayan', 'logo'), exist_ok=True))
        with open(os.path.join(self.media_dir, 'ankurayan', 'logo', seed.YEAR_LOGOS[2020]), 'wb') as fh:
            fh.write(TINY_GIF)

        with OFFLINE:
            run('seed_ankurayan_content', '--offline')

        self.assertFalse(Ankurayan.objects.filter(pk=stale.pk).exists())
        kept.refresh_from_db()
        self.assertEqual(kept.logo.name, 'ankurayan/logo/custom.jpg')
        self.assertEqual(kept.slug, '2024')
        # existing guest name skipped, the other three added
        self.assertEqual(Guest.objects.filter(ankurayan=kept).count(), 4)
        # stale photo not in the synced set is removed
        self.assertFalse(Photo.objects.filter(ankurayan=kept).exists())
        default_logo.refresh_from_db()
        self.assertEqual(default_logo.logo.name, f'ankurayan/logo/{seed.YEAR_LOGOS[2020]}')

    def test_offline_seed_copies_local_img_assets_and_scans_year_folder(self):
        base_dir = os.path.join(self.media_dir, 'fake-base')
        img_dir = os.path.join(base_dir, 'img')
        os.makedirs(img_dir)
        for name in ('Ankurayan_2025_Logo.png', 'punchi.jpg'):
            with open(os.path.join(img_dir, name), 'wb') as fh:
                fh.write(TINY_GIF)
        year_dir = os.path.join(self.media_dir, 'ankurayan', '2011')
        os.makedirs(year_dir)
        for name in ('a.jpg', 'a_AbCdEfG.jpg', 'notes.txt'):
            with open(os.path.join(year_dir, name), 'wb') as fh:
                fh.write(TINY_GIF)

        with OFFLINE, override_settings(BASE_DIR=base_dir):
            out = run('seed_ankurayan_content', '--offline')

        self.assertTrue(os.path.isfile(
            os.path.join(self.media_dir, 'ankurayan', 'index', 'Ankurayan_2025_Logo.png')))
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'ankurayan', '2020', 'punchi.jpg')))
        photo_2018 = Photo.objects.get(ankurayan__year=2018)
        self.assertEqual(photo_2018.picture.name, 'ankurayan/2020/punchi.jpg')
        self.assertTrue(photo_2018.approved)
        self.assertEqual(
            list(Photo.objects.filter(ankurayan__year=2011).values_list('picture', flat=True)),
            ['ankurayan/2011/a.jpg'])
        self.assertIn('synced 2 gallery photo(s)', out)

        with OFFLINE, override_settings(BASE_DIR=base_dir):
            run('seed_ankurayan_content', '--offline')
        # Quirk: YEAR_THEMES processes 2020 before 2018, so on the first run
        # ankurayan/2020/ doesn't exist yet when 2020 is scanned. YEAR_GALLERY[2018]
        # points at 'ankurayan/2020/punchi.jpg', so syncing 2018 later in the same run
        # creates that file under the "2020" folder. On the second run, 2020 is scanned
        # again (now that the folder exists) and _local_year_gallery_paths picks up
        # punchi.jpg as if it belonged to year 2020 too, adding a 3rd Photo row.
        self.assertEqual(
            sorted(Photo.objects.values_list('ankurayan__year', 'picture')),
            [(2011, 'ankurayan/2011/a.jpg'), (2018, 'ankurayan/2020/punchi.jpg'),
             (2020, 'ankurayan/2020/punchi.jpg')],
        )
        self.assertEqual(Photo.objects.count(), 3)

    def test_online_seed_uses_production_html_and_downloads(self):
        def fake_urlopen(request, timeout=None):
            url = request.full_url
            if '/ankurayan/detail/2024/' in url:
                return FakeResponse(PRODUCTION_HTML.encode('utf-8'))
            if '/ankurayan/detail/' in url:
                raise urllib.error.URLError('down')
            if '/media/ankurayan/logo/' in url and 'Logo2019' in url:
                raise urllib.error.URLError('no logo')
            return FakeResponse(TINY_GIF)

        with mock.patch('urllib.request.urlopen', side_effect=fake_urlopen) as urlopen:
            out = run('seed_ankurayan_content')
        self.assertTrue(urlopen.called)
        self.assertIn('synced 1 year page(s)', out)
        self.assertIn('Could not fetch Ankurayan 2025 from production', out)

        a2024 = Ankurayan.objects.get(year=2024)
        self.assertEqual(a2024.description, 'Live description')
        self.assertEqual(a2024.visitors, 'Live visitors')
        self.assertEqual(a2024.logo.name, f'ankurayan/logo/{seed.YEAR_LOGOS[2024]}')
        self.assertEqual(
            set(Guest.objects.filter(ankurayan=a2024).values_list('name', flat=True)),
            {'Live Guest', 'Quiet Guest'})
        self.assertEqual(Guest.objects.get(name='Live Guest').quote, 'It was \'great\' "fun"...')
        self.assertEqual(
            sorted(Photo.objects.filter(ankurayan=a2024).values_list('picture', flat=True)),
            ['ankurayan/2024/one.jpg', 'ankurayan/2024/two.png'])
        self.assertTrue(os.path.isfile(os.path.join(self.media_dir, 'ankurayan', '2024', 'one.jpg')))
        logo_dir = os.path.join(self.media_dir, 'ankurayan', 'logo')
        self.assertTrue(os.path.isfile(os.path.join(logo_dir, seed.YEAR_LOGOS[2024])))
        self.assertFalse(os.path.isfile(os.path.join(logo_dir, 'Logo2019.jpg')))
        # NOTE (app quirk, not fixed here per task scope): the 2019 logo file never gets
        # downloaded (assertFalse above), but the "fall back to default logo if the file
        # doesn't exist" check at seed_ankurayan_content.py ~L431 only fires for a row
        # whose *existing* logo is falsy or literally ends with 'Logo.jpg'. get_or_create's
        # `defaults` already sets logo='ankurayan/logo/Logo2019.jpg' on creation (which
        # doesn't end with 'Logo.jpg'), so the existence check never runs and the Ankurayan
        # row ends up pointing at a logo file that was never actually written.
        self.assertEqual(Ankurayan.objects.get(year=2019).logo.name, 'ankurayan/logo/Logo2019.jpg')
        # The rest of the years fell back to local copy (still seeded)
        self.assertEqual(Ankurayan.objects.count(), len(seed.YEAR_THEMES))
        self.assertEqual(Guest.objects.filter(ankurayan__year=2025).count(), 4)

        # Second run: logos already present are not re-fetched, photos re-used
        with mock.patch('urllib.request.urlopen', side_effect=fake_urlopen) as urlopen:
            run('seed_ankurayan_content')
        fetched = [c.args[0].full_url for c in urlopen.call_args_list]
        self.assertFalse(any(seed.YEAR_LOGOS[2024] in u for u in fetched))
        self.assertEqual(Photo.objects.filter(ankurayan=a2024).count(), 2)


class GuestCommandTests(TestCase):
    def setUp(self):
        self.a2024 = make_ankurayan(2024)
        self.a2020 = make_ankurayan(2020, slug='ankurayan-2020')

    def test_seed_dummy_guests_all_years_and_skip(self):
        out = run('seed_dummy_guests')
        self.assertEqual(Guest.objects.count(), 4)
        self.assertIn('Created 4 guest(s), skipped 0', out)
        out = run('seed_dummy_guests')
        self.assertEqual(Guest.objects.count(), 4)
        self.assertIn('Created 0 guest(s), skipped 4', out)
        guest = Guest.objects.get(ankurayan=self.a2024, name=EXAMPLE_GUESTS[1]['name'])
        self.assertEqual(guest.sort_order, 1)
        self.assertEqual(guest.email, EXAMPLE_GUESTS[1]['email'])

    def test_seed_dummy_guests_filters(self):
        run('seed_dummy_guests', year=2024)
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2024).count(), 2)
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2020).count(), 0)
        run('seed_dummy_guests', slug='ankurayan-2020')
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2020).count(), 2)
        out = run('seed_dummy_guests', year=1900)
        self.assertIn('No Ankurayan rows matched', out)

    def test_reset_example_guests_all(self):
        Guest.objects.create(ankurayan=self.a2024, name='Old', profession='x')
        Guest.objects.create(ankurayan=self.a2020, name='Older', profession='x')
        out = run('reset_example_guests')
        self.assertIn('Removed 2 guest profile(s) total.', out)
        self.assertIn('Done. 4 guest profile(s) across 2 Ankurayan year(s).', out)
        self.assertFalse(Guest.objects.filter(name__in=['Old', 'Older']).exists())
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2024).count(), 2)
        run('reset_example_guests')
        self.assertEqual(Guest.objects.count(), 4)

    def test_reset_example_guests_filtered(self):
        Guest.objects.create(ankurayan=self.a2024, name='Old', profession='x')
        Guest.objects.create(ankurayan=self.a2020, name='Older', profession='x')
        out = run('reset_example_guests', year=2024)
        self.assertIn('Removed 1 guest profile(s) for selected year(s).', out)
        self.assertTrue(Guest.objects.filter(name='Older').exists())
        self.assertFalse(Guest.objects.filter(name='Old').exists())
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2024).count(), 2)
        out = run('reset_example_guests', slug='ankurayan-2020')
        self.assertFalse(Guest.objects.filter(name='Older').exists())
        self.assertEqual(Guest.objects.filter(ankurayan=self.a2020).count(), 2)
        out = run('reset_example_guests', slug='nope')
        self.assertIn('No Ankurayan rows matched', out)
