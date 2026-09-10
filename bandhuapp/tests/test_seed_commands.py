"""Seed commands must be safe to re-run: second run changes nothing and never hits the network."""

import io
import urllib.error
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from applications.anandakendra.models import HomePage as KendraHomePage
from applications.ankurayan.models import HomePage as AnkurayanHomePage
from applications.patriotism import models as patriotism
from applications.prasantaraktadan import models as raktadan
from applications.sevavrata import models as sevavrata
from bandhuapp.management.commands import seed_landing_content
from bandhuapp.models import (
    AboutSlide,
    Contact,
    Designation,
    HeroSlide,
    HomeVisitor,
    RecentActivity,
    SanskarHomePage,
    SanskarHomePhoto,
    Staff,
    SwabalambanHomePage,
    SwarajHomePage,
    Video,
)
from bandhuapp.tests.support import TempMediaMixin


def _offline(*args, **kwargs):
    raise urllib.error.URLError('network disabled in tests')


def run(command, *args):
    out = io.StringIO()
    call_command(command, *args, stdout=out, stderr=out)
    return out.getvalue()


class SeedCommandIdempotencyTests(TempMediaMixin, TestCase):
    def setUp(self):
        patcher = mock.patch('urllib.request.urlopen', side_effect=_offline)
        patcher.start()
        self.addCleanup(patcher.stop)

    def snapshot(self, *models):
        return {f'{model._meta.app_label}.{model.__name__}': model.objects.count() for model in models}

    def assert_idempotent(self, command, models, *args):
        run(command, *args)
        first = self.snapshot(*models)
        run(command, *args)
        self.assertEqual(self.snapshot(*models), first)
        return first

    def test_seed_landing_content(self):
        models = (SanskarHomePage, SwarajHomePage, SwabalambanHomePage, HeroSlide, AboutSlide,
                  Contact, KendraHomePage, AnkurayanHomePage)
        # The command captures MEDIA_ROOT at import time; keep test writes in the temp dir.
        with mock.patch.object(seed_landing_content, 'MEDIA_ROOT', self.media_dir):
            counts = self.assert_idempotent('seed_landing_content', models)
        self.assertEqual(counts['bandhuapp.Contact'], 1)
        for name in ('bandhuapp.SanskarHomePage', 'bandhuapp.SwarajHomePage', 'bandhuapp.SwabalambanHomePage'):
            self.assertLessEqual(counts[name], 1, name)
        # Only pillars whose bundled source image exists get a page (swaraj ships our_mission1.jpg).
        self.assertEqual(counts['bandhuapp.SwarajHomePage'], 1)
        self.assertEqual(SwarajHomePage.objects.get().tagline, 'For the common man...')
        self.assertEqual(counts['anandakendra.HomePage'], 1)
        self.assertEqual(counts['ankurayan.HomePage'], 1)

    def test_seed_sanskar_content(self):
        counts = self.assert_idempotent('seed_sanskar_content', (SanskarHomePage, SanskarHomePhoto))
        self.assertEqual(counts['bandhuapp.SanskarHomePage'], 1)
        page = SanskarHomePage.objects.get()
        self.assertEqual(page.tagline, 'Anandakendra and Ankurayan')
        self.assertTrue(page.image_caption_en)

    def test_seed_initiative_program_homepages(self):
        for command, models in (
            ('seed_prasantaraktadan_content', raktadan),
            ('seed_patriotism_content', patriotism),
            ('seed_sevavrata_content', sevavrata),
        ):
            with self.subTest(command=command):
                counts = self.assert_idempotent(command, (models.HomePage, models.Ashram))
                self.assertEqual(counts[f'{models.HomePage._meta.app_label}.HomePage'], 1)
                self.assertTrue(models.HomePage.objects.get().tagline)

    def test_seed_initiative_program_clear_flag_wipes_year_entries(self):
        raktadan.Ashram.objects.create(
            name='Old', locality='Cuttack', description='d', address='a', image='t/h.gif', slug='old',
        )
        output = run('seed_prasantaraktadan_content', '--clear')
        self.assertEqual(raktadan.Ashram.objects.count(), 0)
        self.assertEqual(raktadan.HomePage.objects.count(), 1)
        self.assertIn('0 year entr', output)

    def test_seed_landing_notices(self):
        counts = self.assert_idempotent('seed_landing_notices', (RecentActivity,))
        self.assertGreater(counts['bandhuapp.RecentActivity'], 0)

    def test_seed_landing_videos(self):
        counts = self.assert_idempotent('seed_landing_videos', (Video,))
        self.assertGreater(counts['bandhuapp.Video'], 0)

    def test_seed_home_visitors(self):
        counts = self.assert_idempotent('seed_home_visitors', (HomeVisitor,))
        self.assertGreater(counts['bandhuapp.HomeVisitor'], 0)
        run('seed_home_visitors', '--force')
        self.assertEqual(HomeVisitor.objects.count(), counts['bandhuapp.HomeVisitor'])

    def test_seed_dummy_people_requires_designations(self):
        output = run('seed_dummy_people')
        self.assertEqual(Staff.objects.count(), 0)
        self.assertIn('seed_people', output)

    def test_seed_dummy_people(self):
        Designation.objects.create(title='Core Team', rank=1)
        Designation.objects.create(title='Office Bearers', rank=2)
        counts = self.assert_idempotent('seed_dummy_people', (Staff,))
        self.assertEqual(counts['bandhuapp.Staff'], 2)
