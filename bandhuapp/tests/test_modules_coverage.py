"""Coverage for small bandhuapp helper modules: template filters, annual report
serialisers, the initiative-activity migration helper, the initiatives-section
payload builder, and notice-link resolution."""

from unittest import mock

from django.test import RequestFactory, TestCase
from django.urls import reverse

from applications.ankurayan.models import HomePage as AnkurayanHomePage
from applications.ashram.models import HomePage as AshramHomePage
from applications.charitywork.models import HomePage as CharityHomePage
from bandhuapp import annual_reports, initiative_activity_migrate, initiatives_section, notice_links
from bandhuapp.models import AnnualReport
from bandhuapp.templatetags import custom_filters
from bandhuapp.tests.support import TempMediaMixin, image_upload


# --------------------------------------------------------------------------- custom_filters

class CustomFiltersTests(TestCase):
    def test_proper_case_filter(self):
        self.assertEqual(custom_filters.proper_case_filter('hello world'), 'Hello World')

    def test_proper_case_lines_preserves_blank_lines(self):
        value = 'hello world\n\nfoo bar'
        self.assertEqual(custom_filters.proper_case_lines(value), 'Hello World\n\nFoo Bar')

    def test_proper_case_lines_none_returns_empty(self):
        self.assertEqual(custom_filters.proper_case_lines(None), '')

    def test_proper_case_lines_non_string_is_stringified(self):
        self.assertEqual(custom_filters.proper_case_lines(2024), '2024')

    def test_avoid_orphan_sincerity_wraps_matching_closing_sentence(self):
        value = 'About Bandhu does small things with the highest possible sincerity.'
        result = custom_filters.avoid_orphan_sincerity(value)
        self.assertIn('about-desc-closing', result)
        self.assertTrue(result.startswith('About Bandhu<p'))

    def test_avoid_orphan_sincerity_returns_original_when_no_match(self):
        value = 'Some unrelated closing line.'
        self.assertEqual(custom_filters.avoid_orphan_sincerity(value), value)

    def test_avoid_orphan_sincerity_none_and_non_string(self):
        self.assertEqual(custom_filters.avoid_orphan_sincerity(None), '')
        self.assertEqual(custom_filters.avoid_orphan_sincerity(5), '5')

    def test_single_line_collapses_breaks_and_spaces(self):
        value = 'Line one\r\nLine   two\nLine  three\r'
        self.assertEqual(custom_filters.single_line(value), 'Line one Line two Line three')

    def test_single_line_none_and_non_string(self):
        self.assertEqual(custom_filters.single_line(None), '')
        self.assertEqual(custom_filters.single_line(7), '7')

    def test_to_snake_case(self):
        self.assertEqual(custom_filters.to_snake_case('Hello World'), 'hello-world')

    def test_null_to_hyphen(self):
        self.assertEqual(custom_filters.null_to_hyphen(''), '-')
        self.assertEqual(custom_filters.null_to_hyphen(None), '-')
        self.assertEqual(custom_filters.null_to_hyphen('value'), 'value')

    def test_profession_lines_blank_profession(self):
        self.assertEqual(custom_filters.profession_lines('', 'Office Bearers'), [''])

    def test_profession_lines_office_bearer_splits_last_comma(self):
        result = custom_filters.profession_lines(
            'Joint Secretary, Social Media Manager', 'Office Bearers'
        )
        self.assertEqual(result, ['Joint Secretary', 'Social Media Manager'])

    def test_profession_lines_office_bearer_without_comma(self):
        result = custom_filters.profession_lines('President', 'Office Bearers')
        self.assertEqual(result, ['President'])

    def test_profession_lines_non_office_bearer_stays_single_line(self):
        result = custom_filters.profession_lines('Teacher, Volunteer', 'Core Team')
        self.assertEqual(result, ['Teacher, Volunteer'])


# --------------------------------------------------------------------------- annual_reports

class AnnualReportsSerializerTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_annual_reports_upload_url_normal(self):
        expected = reverse('annual_reports_upload')
        self.assertEqual(annual_reports.annual_reports_upload_url(), expected)

    def test_annual_reports_upload_url_falls_back_when_reverse_fails(self):
        with mock.patch('django.urls.reverse', side_effect=Exception('boom')):
            result = annual_reports.annual_reports_upload_url()
        self.assertEqual(result, annual_reports.ANNUAL_REPORTS_UPLOAD_PATH)

    def test_serialize_annual_reports_public(self):
        AnnualReport.objects.create(year=2024, pdf_file=None, external_url='https://example.com/a.pdf')
        AnnualReport.objects.create(year=2023, is_published=False, external_url='https://example.com/b.pdf')
        request = self.factory.get('/')
        items = annual_reports.serialize_annual_reports(request)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['year'], 2024)
        self.assertTrue(items[0]['is_external'])

    def test_serialize_annual_reports_skips_report_with_no_url(self):
        report = AnnualReport(year=2020, is_published=True)
        report.save()
        request = self.factory.get('/')
        items = annual_reports.serialize_annual_reports(request)
        self.assertEqual(items, [])

    def test_serialize_annual_reports_admin_includes_unpublished(self):
        AnnualReport.objects.create(year=2024, external_url='https://example.com/a.pdf')
        AnnualReport.objects.create(
            year=2023, is_published=False, external_url='https://example.com/b.pdf'
        )
        request = self.factory.get('/')
        items = annual_reports.serialize_annual_reports_admin(request)
        self.assertEqual(len(items), 2)
        years = {item['year'] for item in items}
        self.assertEqual(years, {2024, 2023})

    def test_is_annual_report_ajax_by_query_param(self):
        request = self.factory.get('/?format=json')
        self.assertTrue(annual_reports.is_annual_report_ajax(request))

    def test_is_annual_report_ajax_by_header(self):
        request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(annual_reports.is_annual_report_ajax(request))

    def test_is_annual_report_ajax_false_for_plain_request(self):
        request = self.factory.get('/')
        self.assertFalse(annual_reports.is_annual_report_ajax(request))


# --------------------------------------------------------------------------- initiative_activity_migrate

class _FakeQuerySet(list):
    def update(self, **kwargs):
        for obj in self:
            for key, value in kwargs.items():
                setattr(obj, key, value)
        return len(self)


class _FakeManager:
    def __init__(self, objects):
        self._objects = objects

    def select_related(self, *args, **kwargs):
        return self

    def iterator(self):
        return iter(list(self._objects))

    def all(self):
        return _FakeQuerySet(self._objects)

    def filter(self, **kwargs):
        return _FakeQuerySet(
            o for o in self._objects
            if all(getattr(o, k, None) == v for k, v in kwargs.items())
        )


class _FakeCategoryWithAshram:
    def __init__(self, id, name, ashram_id=None):
        self.id = id
        self.name = name
        self.ashram_id = ashram_id
        self.deleted = False

    def delete(self):
        self.deleted = True


class _FakeCategoryWithoutAshram:
    """Simulates a program-wide category that never had an `ashram` field."""

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.deleted = False

    def delete(self):
        self.deleted = True


class _FakeActivity:
    def __init__(self, id, category, ashram_id=None):
        self.id = id
        self.category = category
        self.category_id = category.id
        self.ashram_id = ashram_id
        self.save_calls = []

    def save(self, update_fields=None):
        self.save_calls.append(update_fields)


class _FakeModel:
    """A stand-in for a historical `apps.get_model()` model class."""

    def __init__(self, objects):
        self.objects = _FakeManager(objects)


class _FakeApps:
    def __init__(self, models):
        self._models = models

    def get_model(self, app_label, name):
        return self._models[name]


class InitiativeActivityMigrateTests(TestCase):
    def test_backfills_activity_ashram_from_category_and_dedupes(self):
        keeper = _FakeCategoryWithAshram(1, 'Health', ashram_id=10)
        duplicate = _FakeCategoryWithAshram(2, 'Health', ashram_id=20)
        untouched = _FakeCategoryWithAshram(3, 'Education', ashram_id=None)
        no_ashram_field = _FakeCategoryWithoutAshram(4, 'Sports')

        activity_needs_backfill = _FakeActivity(1, keeper, ashram_id=None)
        activity_already_set = _FakeActivity(2, keeper, ashram_id=99)
        activity_on_duplicate = _FakeActivity(3, duplicate, ashram_id=None)
        activity_no_ashram_field_category = _FakeActivity(4, no_ashram_field, ashram_id=None)

        activities = [
            activity_needs_backfill,
            activity_already_set,
            activity_on_duplicate,
            activity_no_ashram_field_category,
        ]
        categories = [keeper, duplicate, untouched, no_ashram_field]

        apps = _FakeApps({
            'Activity': _FakeModel(activities),
            'ActivityCategory': _FakeModel(categories),
        })

        initiative_activity_migrate.migrate_activity_categories_to_program_scope(
            apps, None, 'someapp'
        )

        # backfilled from its (truthy) category ashram_id
        self.assertEqual(activity_needs_backfill.ashram_id, 10)
        self.assertEqual(activity_needs_backfill.save_calls, [['ashram_id']])

        # already had an ashram_id: left untouched, no save() call
        self.assertEqual(activity_already_set.ashram_id, 99)
        self.assertEqual(activity_already_set.save_calls, [])

        # category without the ashram_id attribute at all: no crash, no backfill
        self.assertIsNone(activity_no_ashram_field_category.ashram_id)
        self.assertEqual(activity_no_ashram_field_category.save_calls, [])

        # duplicate-named category merged into the first ("keeper") category
        self.assertTrue(duplicate.deleted)
        self.assertFalse(keeper.deleted)
        self.assertFalse(untouched.deleted)
        self.assertEqual(activity_on_duplicate.category_id, keeper.id)


# --------------------------------------------------------------------------- initiatives_section

class InitiativesSectionTests(TempMediaMixin, TestCase):
    def test_returns_none_when_no_home_pages_have_content(self):
        payload = initiatives_section.build_initiatives_payload(lambda field: None)
        self.assertIsNone(payload)

    def test_returns_payload_when_a_home_page_has_a_description(self):
        AshramHomePage.objects.create(tagline='Tag', description='A shelter for all.')
        payload = initiatives_section.build_initiatives_payload(lambda field: None)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['bandhughar_desc'], 'A shelter for all.')
        self.assertIsNone(payload['bandhughar_thumb'])
        self.assertEqual(payload['kendra_desc'], '')

    def test_description_falls_back_to_tagline_and_file_url_is_used(self):
        CharityHomePage.objects.create(tagline='Helping hands', description='', picture=image_upload())

        def file_url(field):
            if field and getattr(field, 'name', None):
                return f'/media/{field.name}'
            return None

        payload = initiatives_section.build_initiatives_payload(file_url)
        self.assertEqual(payload['otheract_desc'], 'Helping hands')
        self.assertTrue(payload['otheract_thumb'].startswith('/media/'))

    def test_multiple_home_pages_populate_independently(self):
        AnkurayanHomePage.objects.create(tagline='', description='Youth programs.')
        AshramHomePage.objects.create(tagline='', description='Shelter info.')
        payload = initiatives_section.build_initiatives_payload(lambda field: None)
        self.assertEqual(payload['ankurayan_desc'], 'Youth programs.')
        self.assertEqual(payload['bandhughar_desc'], 'Shelter info.')


# --------------------------------------------------------------------------- notice_links

class NoticeLinksTests(TestCase):
    def test_blank_or_missing_url_returns_none(self):
        self.assertIsNone(notice_links.resolve_notice_url('some text', None))
        self.assertIsNone(notice_links.resolve_notice_url('some text', '  '))

    def test_hash_url_passthrough(self):
        self.assertEqual(notice_links.resolve_notice_url('some text', '#'), '#')

    def test_legacy_other_activities_rewritten(self):
        expected = reverse('charitywork:charity_work')
        result = notice_links.resolve_notice_url(
            'Other activities', 'https://bandhuodisha.in/other_activities/'
        )
        self.assertEqual(result, expected)

    def test_legacy_root_rewritten_to_slash(self):
        result = notice_links.resolve_notice_url('Home', 'https://www.bandhuodisha.in/')
        self.assertEqual(result, '/')

    def test_legacy_other_path_preserves_query_string(self):
        result = notice_links.resolve_notice_url(
            'Gallery', 'https://bandhuodisha.in/gallery/photos?tag=x'
        )
        self.assertEqual(result, '/gallery/photos?tag=x')

    def test_legacy_ankurayan_list_with_year_resolves_to_existing_detail(self):
        ankurayan_app = __import__(
            'applications.ankurayan.models', fromlist=['Ankurayan']
        ).Ankurayan
        ankurayan_app.objects.create(
            year=2021,
            title='Ankurayan 2021',
            theme='Theme',
            description='Desc',
            start_date='2021-01-01',
            end_date='2021-01-05',
            slug='ankurayan-2021',
        )
        result = notice_links.resolve_notice_url(
            'Ankurayan Utsav 2021', 'https://bandhuodisha.in/ankurayan/'
        )
        expected = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': 'ankurayan-2021'})
        self.assertEqual(result, expected)

    def test_generic_ankurayan_list_with_year_but_no_matching_entry_falls_back_to_list(self):
        result = notice_links.resolve_notice_url('Ankurayan Utsav 2019', '/ankurayan')
        expected = reverse('ankurayan:ankurayan')
        self.assertEqual(result, expected)

    def test_generic_ankurayan_list_without_year_falls_back_to_list(self):
        result = notice_links.resolve_notice_url('', '/ankurayan')
        expected = reverse('ankurayan:ankurayan')
        self.assertEqual(result, expected)

    def test_leading_slash_path_passthrough(self):
        result = notice_links.resolve_notice_url('Some notice', '/some/other/path/')
        self.assertEqual(result, '/some/other/path/')

    def test_absolute_external_url_passthrough(self):
        result = notice_links.resolve_notice_url('External', 'https://example.com/x')
        self.assertEqual(result, 'https://example.com/x')

    def test_bare_string_without_scheme_or_slash_passthrough(self):
        result = notice_links.resolve_notice_url('Notice', 'contact-office')
        self.assertEqual(result, 'contact-office')
