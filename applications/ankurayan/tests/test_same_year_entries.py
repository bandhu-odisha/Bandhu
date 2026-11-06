"""Two Ankurayan rows in one year (e.g. a special "Jan 2015" next to Dec 2015)."""

import io
import shutil
import tempfile
import urllib.error
from datetime import date
from unittest import mock

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from bandhuapp.tests.support import PASSWORD, TempMediaMixin, image_upload, make_admin
from applications.ankurayan.management.commands.seed_ankurayan_content import (
    delete_unsynced_unlabelled,
    find_or_create_ankurayan,
)
from applications.ankurayan.models import Ankurayan, AnkurayanInvitationLetter, HomePage


def make_entry(year, slug, start, label='', **overrides):
    data = dict(
        year=year, label=label, title=f'Ankurayan {year}', theme='T', description='D',
        start_date=start, end_date=start, logo=image_upload('logo.gif'), slug=slug,
    )
    data.update(overrides)
    return Ankurayan.objects.create(**data)


def make_dec_and_jan(jan_first=False):
    jan_kwargs = dict(year=2015, slug='2015-jan', start=date(2015, 1, 10), label='Jan 2015')
    dec_kwargs = dict(year=2015, slug='2015', start=date(2015, 12, 17), label='Dec 2015')
    if jan_first:
        jan = make_entry(**jan_kwargs)
        dec = make_entry(**dec_kwargs)
    else:
        dec = make_entry(**dec_kwargs)
        jan = make_entry(**jan_kwargs)
    return dec, jan


class ModelTests(TempMediaMixin, TestCase):
    def test_two_entries_share_a_year(self):
        make_dec_and_jan()
        self.assertEqual(Ankurayan.objects.filter(year=2015).count(), 2)

    def test_duplicate_slug_rejected(self):
        make_entry(2015, '2015', date(2015, 12, 17))
        with self.assertRaises(IntegrityError), transaction.atomic():
            make_entry(2016, '2015', date(2016, 12, 17))

    def test_display_label_and_str(self):
        plain = make_entry(2014, '2014', date(2014, 12, 17))
        special = make_entry(2015, '2015-jan', date(2015, 1, 10), label='Jan 2015')
        self.assertEqual(plain.display_label, '2014')
        self.assertEqual(str(plain), 'Ankurayan 2014')
        self.assertEqual(special.display_label, 'Jan 2015')
        self.assertEqual(str(special), 'Ankurayan Jan 2015')
        letter = AnkurayanInvitationLetter(ankurayan=special)
        self.assertEqual(str(letter), 'Invitation letter — Ankurayan Jan 2015')
        self.assertEqual(
            str(AnkurayanInvitationLetter(ankurayan=plain)), 'Invitation letter — Ankurayan 2014')


class OrderingTests(TempMediaMixin, TestCase):
    def check_index_order(self, jan_first):
        make_dec_and_jan(jan_first=jan_first)
        make_entry(2016, '2016', date(2016, 12, 17))
        response = self.client.get('/ankurayan/')
        self.assertEqual(
            [a.slug for a in response.context['ankurayans']], ['2016', '2015', '2015-jan'])

    def test_index_dec_before_jan_when_jan_inserted_last(self):
        self.check_index_order(jan_first=False)

    def test_index_dec_before_jan_when_jan_inserted_first(self):
        self.check_index_order(jan_first=True)

    def test_detail_sidebar_list_orders_same_year_by_start_date(self):
        for jan_first in (False, True):
            Ankurayan.objects.all().delete()
            make_dec_and_jan(jan_first=jan_first)
            make_entry(2016, '2016', date(2016, 12, 17))
            response = self.client.get('/ankurayan/detail/2016/')
            self.assertEqual(
                [a.slug for a in response.context['ankurayans']], ['2015', '2015-jan'])


class LabelRenderingTests(TempMediaMixin, TestCase):
    def test_both_detail_pages_render_their_own_label(self):
        make_dec_and_jan()
        jan = self.client.get('/ankurayan/detail/2015-jan/')
        dec = self.client.get('/ankurayan/detail/2015/')
        self.assertEqual(jan.status_code, 200)
        self.assertEqual(dec.status_code, 200)
        jan_html, dec_html = jan.content.decode(), dec.content.decode()
        self.assertIn('<h1 class="bold-txt page-showcase-title">Ankurayan Jan 2015</h1>', jan_html)
        self.assertIn('content: "Ankurayan Jan 2015"', jan_html)
        self.assertIn('Ankurayan Jan 2015', jan_html.split('<title>')[1].split('</title>')[0])
        self.assertNotIn('<h1 class="bold-txt page-showcase-title">Ankurayan 2015</h1>', jan_html)
        self.assertIn('<h1 class="bold-txt page-showcase-title">Ankurayan Dec 2015</h1>', dec_html)
        self.assertNotIn('Ankurayan Jan 2015</h1>', dec_html)

    def test_invitation_letter_text_uses_label(self):
        jan = make_entry(2015, '2015-jan', date(2015, 1, 10), label='Jan 2015')
        AnkurayanInvitationLetter.objects.create(ankurayan=jan, file='ankurayan/invitation_letters/i.pdf')
        html = self.client.get('/ankurayan/detail/2015-jan/').content.decode()
        self.assertIn('Invitation letter — Ankurayan Jan 2015', html)
        self.assertNotIn('Invitation letter — Ankurayan 2015<', html)

    def test_index_chips_show_labels(self):
        HomePage.objects.create(tagline='Tag', description='Home desc')  # chips render only with page content
        make_dec_and_jan()
        html = self.client.get('/ankurayan/').content.decode()
        self.assertIn('aria-label="Ankurayan Jan 2015">Jan 2015</a>', html)
        self.assertIn('aria-label="Ankurayan Dec 2015">Dec 2015</a>', html)
        self.assertIn('/ankurayan/detail/2015-jan/', html)

    def test_blank_label_renders_year_as_before(self):
        make_entry(2015, '2015', date(2015, 12, 17))
        html = self.client.get('/ankurayan/detail/2015/').content.decode()
        self.assertIn('<h1 class="bold-txt page-showcase-title">Ankurayan 2015</h1>', html)
        HomePage.objects.create(tagline='Tag', description='Home desc')
        index = self.client.get('/ankurayan/').content.decode()
        self.assertIn('aria-label="Ankurayan 2015">2015</a>', index)


class AdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.login(email='admin@example.com', password=PASSWORD)

    def post(self, **overrides):
        data = {
            'year': '2015', 'label': 'Jan 2015', 'title': 'Ankurayan Jan 2015', 'theme': 'T',
            'slug': '2015-jan', 'start_date': '2015-01-10', 'end_date': '2015-01-12',
            'logo': image_upload(), 'description': 'D', 'reports': '', 'publications': '',
            'visitors': '', 'image_caption_en': '', 'image_caption_or': '',
        }
        data.update(overrides)
        return self.client.post(reverse('admin:ankurayan_ankurayan_add'), data)

    def test_second_entry_in_same_year_can_be_added(self):
        make_entry(2015, '2015', date(2015, 12, 17))
        response = self.post()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ankurayan.objects.get(slug='2015-jan').label, 'Jan 2015')

    def test_clashing_slug_is_a_form_error_not_a_duplicate(self):
        make_entry(2015, '2015', date(2015, 12, 17))
        response = self.post(slug='2015')
        self.assertEqual(response.status_code, 200)
        self.assertIn('slug', response.context['adminform'].form.errors)
        self.assertEqual(Ankurayan.objects.filter(slug='2015').count(), 1)
        self.assertEqual(Ankurayan.objects.count(), 1)

    def test_add_form_has_label_and_changelist_shows_it(self):
        make_entry(2015, '2015', date(2015, 12, 17), label='Dec 2015')
        form = self.client.get(reverse('admin:ankurayan_ankurayan_add'))
        self.assertIn('label', form.context['adminform'].form.fields)
        listing = self.client.get(reverse('admin:ankurayan_ankurayan_changelist'))
        self.assertContains(listing, 'Dec 2015')

    def test_changelist_orders_by_year_then_start_date(self):
        for jan_first in (False, True):
            with self.subTest(jan_first=jan_first):
                Ankurayan.objects.all().delete()
                make_dec_and_jan(jan_first=jan_first)
                listing = self.client.get(reverse('admin:ankurayan_ankurayan_changelist'))
                self.assertEqual(
                    [a.slug for a in listing.context['cl'].result_list], ['2015-jan', '2015'])


class SeedLookupTests(TempMediaMixin, TestCase):
    defaults = dict(title='t', theme='T', description='D', start_date=date(2015, 12, 17),
                    end_date=date(2015, 12, 19), slug='2015')

    def test_prefers_row_slugged_with_the_year(self):
        dec, jan = make_dec_and_jan(jan_first=True)
        self.assertEqual(find_or_create_ankurayan(2015, dict(self.defaults, logo='x.jpg')), dec)
        self.assertEqual(Ankurayan.objects.count(), 2)

    def test_single_row_with_other_slug_is_reused(self):
        only = make_entry(2015, 'old-slug', date(2015, 12, 17))
        self.assertEqual(find_or_create_ankurayan(2015, dict(self.defaults, logo='x.jpg')), only)
        self.assertEqual(Ankurayan.objects.count(), 1)

    def test_lone_labelled_row_is_not_reused(self):
        special = make_entry(2015, '2015-jan', date(2015, 1, 10), label='Jan 2015')
        row = find_or_create_ankurayan(2015, dict(self.defaults, logo='x.jpg'))
        self.assertNotEqual(row, special)
        self.assertEqual(row.slug, '2015')
        self.assertEqual(Ankurayan.objects.count(), 2)

    def test_creates_when_year_has_no_row(self):
        row = find_or_create_ankurayan(2015, dict(self.defaults, logo='x.jpg'))
        self.assertEqual((row.year, row.slug), (2015, '2015'))
        self.assertEqual(Ankurayan.objects.count(), 1)


class SeedCleanupTests(TempMediaMixin, TestCase):
    def test_labelled_unsynced_row_survives_and_unlabelled_is_deleted(self):
        kept = make_entry(2015, '2015', date(2015, 12, 17))
        special = make_entry(2015, '2015-jan', date(2015, 1, 10), label='Jan 2015')
        stale = make_entry(2014, '2014', date(2014, 12, 17))
        delete_unsynced_unlabelled([kept.id])
        self.assertEqual(
            set(Ankurayan.objects.values_list('id', flat=True)), {kept.id, special.id})
        self.assertFalse(Ankurayan.objects.filter(id=stale.id).exists())


class SeedCommandTests(TempMediaMixin, TestCase):
    """End to end: ``seed_ankurayan_content --offline`` with two 2015 rows."""

    def run_seed(self):
        empty = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty, True)
        offline = mock.patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline'))
        with offline, override_settings(MEDIA_ROOT=empty):
            call_command('seed_ankurayan_content', '--offline', stdout=io.StringIO())

    def test_seed_offline_keeps_both_2015_rows(self):
        dec = make_entry(2015, '2015', date(2015, 12, 17), label='Dec 2015', title='keep-title')
        jan = make_entry(2015, '2015-jan', date(2015, 1, 10), label='Jan 2015', title='keep-title')
        self.run_seed()
        jan.refresh_from_db()
        dec.refresh_from_db()
        self.assertEqual((jan.slug, jan.title, jan.label, jan.start_date),
                         ('2015-jan', 'keep-title', 'Jan 2015', date(2015, 1, 10)))
        self.assertEqual((dec.slug, dec.label), ('2015', 'Dec 2015'))
        self.assertEqual(dec.title, 'Ankurayan 2015')
