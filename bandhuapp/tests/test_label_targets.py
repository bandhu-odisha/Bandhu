"""Every <label for="X"> in the on-page admin forms must point at a real id="X"),
and no id may be reused within one rendered page (a `<label for>` resolves to
the FIRST matching id, so a duplicate silently mistargets every later label).

Covers the pages named in planning/2026-09-18-ux-review-fixes/spec.md A8 bullet 2:
anandakendra index + detail, bandhughar (ashram) detail, other_activities (charity)
index + detail, and ankurayan index + detail (F2/F3 of the 2026-09-18 UX review
fixes: duplicate `id="inputGroupFile04"` across these pages). The on-page admin
markup only renders for `is_admin` users, so we log in as one for every page.

Ashram, anandakendra, and ankurayan detail pages each render a "Select
Winners" / activity modal once per activity; ankurayan's activity loop is
additionally nested inside a category loop
(`{% for category %}{% for activity in category.activities.all %}`), so a
naive `id="...{{forloop.counter}}"` resets per category and collides across
categories. We seed two categories with one activity each (not one category
with two activities) so that scenario is actually exercised, plus two
activities under a single category for ashram/anandakendra so their
per-activity loops render more than once too.
"""

from datetime import date
from html.parser import HTMLParser

from django.test import TestCase

from applications.anandakendra.models import (
    ActivityCategory as KendraActivityCategory,
    Activity as KendraActivity,
    AnandaKendra,
)
from applications.ankurayan.models import (
    ActivityCategory as AnkurayanActivityCategory,
    Activity as AnkurayanActivity,
    Ankurayan,
)
from applications.ashram.models import (
    ActivityCategory as AshramActivityCategory,
    Activity as AshramActivity,
    Ashram,
)
from applications.charitywork.models import Charity
from bandhuapp.tests.support import TempMediaMixin, image_upload, make_admin


class LabelCollector(HTMLParser):
    """Collects every element id occurrence (not deduped) and every label[for] value."""

    def __init__(self):
        super().__init__()
        self.id_occurrences = []
        self.label_fors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs and attrs['id']:
            self.id_occurrences.append(attrs['id'])
        if tag == 'label' and 'for' in attrs:
            self.label_fors.append(attrs['for'])


class LabelTargetsTests(TempMediaMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.kendra = AnandaKendra.objects.create(
            name='Test Kendra', locality='Cuttack', slug='test-kendra',
            description='d', address='a', image=image_upload('kendra.gif'),
        )
        kendra_cat = KendraActivityCategory.objects.create(kendra=cls.kendra, name='Category')
        KendraActivity.objects.create(category=kendra_cat, name='Activity 1', description='d', activity_time='10am')
        KendraActivity.objects.create(category=kendra_cat, name='Activity 2', description='d', activity_time='11am')

        cls.ashram = Ashram.objects.create(
            name='Test Bandhughar', locality='Puri', slug='test-bandhughar',
            description='d', address='a', image=image_upload('ashram.gif'),
        )
        ashram_cat = AshramActivityCategory.objects.create(ashram=cls.ashram, name='Category')
        AshramActivity.objects.create(category=ashram_cat, name='Activity 1', description='d')
        AshramActivity.objects.create(category=ashram_cat, name='Activity 2', description='d')

        cls.charity = Charity.objects.create(
            title='Test Charity', purpose='Flood relief', location='Bhubaneswar',
            slug='test-charity', description='d', image=image_upload('charity.gif'),
        )

        cls.ankurayan = Ankurayan.objects.create(
            year=2026, title='Test Ankurayan', theme='t', description='d',
            start_date=date(2026, 1, 1), end_date=date(2026, 1, 2),
            logo=image_upload('ankurayan.gif'), slug='test-ankurayan-2026',
        )
        # Two categories with one activity each: this is what exercises the
        # forloop.counter-reset-per-category risk that a naive rename would miss.
        cat1 = AnkurayanActivityCategory.objects.create(ankurayan=cls.ankurayan, name='Category 1')
        cat2 = AnkurayanActivityCategory.objects.create(ankurayan=cls.ankurayan, name='Category 2')
        AnkurayanActivity.objects.create(category=cat1, name='Activity 1', description='d', date=date(2026, 1, 1))
        AnkurayanActivity.objects.create(category=cat2, name='Activity 2', description='d', date=date(2026, 1, 1))

    def setUp(self):
        self.client.force_login(make_admin())

    def assert_labels_resolve(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        parser = LabelCollector()
        parser.feed(response.content.decode())

        # Restrict the duplicate-id assertion to ids a label[for] actually
        # targets (non-empty `for=`). ankurayan_detail.html separately has
        # duplicate ids that are NOT label targets (e.g. `exampleModalLongTitle`
        # and `mission-carousel` on several unrelated modal titles/carousels)
        # — known pre-existing duplicates, out of scope here.
        referenced_ids = {target for target in parser.label_fors if target}
        ids_seen = {}
        for occurrence in parser.id_occurrences:
            ids_seen[occurrence] = ids_seen.get(occurrence, 0) + 1
        duplicates = {
            i: n for i, n in ids_seen.items() if n > 1 and i in referenced_ids
        }
        self.assertFalse(duplicates, f'{url}: duplicate id(s) referenced by a label on page: {duplicates}')

        ids = set(parser.id_occurrences)
        for target in parser.label_fors:
            # Every label[for] must be non-empty and resolve to a real id.
            self.assertTrue(target, f'{url}: <label for=""> (empty target)')
            self.assertIn(target, ids, f'{url}: <label for="{target}"> has no matching id')

    def test_anandakendra_index(self):
        self.assert_labels_resolve('/anandakendra/')

    def test_anandakendra_detail(self):
        self.assert_labels_resolve(f'/anandakendra/detail/{self.kendra.slug}/')

    def test_bandhughar_detail(self):
        self.assert_labels_resolve(f'/bandhughar/detail/{self.ashram.slug}/')

    def test_other_activities_index(self):
        self.assert_labels_resolve('/other_activities/')

    def test_other_activities_detail(self):
        self.assert_labels_resolve(f'/other_activities/detail/{self.charity.slug}/')

    def test_ankurayan_index(self):
        self.assert_labels_resolve('/ankurayan/')

    def test_ankurayan_detail(self):
        self.assert_labels_resolve(f'/ankurayan/detail/{self.ankurayan.slug}/')
