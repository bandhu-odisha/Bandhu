from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from accounts.models import User
from bandhuapp.models import (
    AnnualReport,
    Designation,
    HomePage,
    SanskarHomePage,
    Staff,
    SwabalambanHomePage,
    SwarajHomePage,
)
from bandhuapp.tests.support import TempMediaMixin, file_upload, make_profile, make_user


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email_and_sets_password(self):
        user = User.objects.create_user('Person@Example.COM', 'secret-123')
        self.assertEqual(user.email, 'Person@example.com')
        self.assertTrue(user.check_password('secret-123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.auth)

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'secret-123')

    def test_create_staffuser_and_superuser_flags(self):
        staff = User.objects.create_staffuser('staff@example.com', 'secret-123')
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_admin)
        root = User.objects.create_superuser('root@example.com', 'secret-123')
        self.assertTrue(root.is_staff)
        self.assertTrue(root.is_admin)

    def test_email_is_unique(self):
        make_user('dup@example.com')
        with self.assertRaises(Exception):
            make_user('dup@example.com')

    def test_string_names_and_flag_properties(self):
        user = make_user('who@example.com', is_staff=True, is_admin=True)
        self.assertEqual(str(user), 'who@example.com')
        self.assertEqual(user.get_full_name(), 'who@example.com')
        self.assertEqual(user.get_short_name(), 'who@example.com')
        self.assertTrue(user.if_staff)
        self.assertTrue(user.if_admin)
        self.assertTrue(user.if_active)
        self.assertTrue(user.has_perm('anything'))
        self.assertTrue(user.has_module_perms('bandhuapp'))


class ProfileTests(TestCase):
    def test_save_applies_proper_case(self):
        profile = make_profile(make_user(), first_name='rAJ', last_name='kumar', city='cuttack')
        self.assertEqual(profile.first_name, 'Raj')
        self.assertEqual(profile.last_name, 'Kumar')
        self.assertEqual(profile.city, 'Cuttack')
        self.assertEqual(profile.get_full_name, 'Raj Kumar')

    def test_complete_address_with_and_without_line_two(self):
        profile = make_profile(make_user(), street_address1='1 main st', street_address2='')
        self.assertEqual(profile.get_complete_address, '1 Main St, Cuttack - 753001, Odisha')
        profile.street_address2 = 'near temple'
        profile.save()
        self.assertEqual(profile.get_complete_address, '1 Main St, Near Temple, Cuttack - 753001, Odisha')

    def test_str_includes_email(self):
        profile = make_profile(make_user('p@example.com'))
        self.assertEqual(str(profile), 'Test Member - p@example.com')

    def test_deleting_user_cascades_to_profile_and_staff(self):
        user = make_user()
        profile = make_profile(user)
        Staff.objects.create(profile=profile, about='x')
        user.delete()
        self.assertEqual(Staff.objects.count(), 0)


class AnnualReportTests(TempMediaMixin, TestCase):
    def test_clean_requires_pdf_or_external_link(self):
        with self.assertRaises(ValidationError):
            AnnualReport(year=2024).clean()
        AnnualReport(year=2024, external_url='https://example.com/r.pdf').clean()

    def test_display_title_defaults_to_year(self):
        self.assertEqual(AnnualReport(year=2024).display_title(), 'Annual Report 2024')
        self.assertEqual(AnnualReport(year=2024, title=' FY 23-24 ').display_title(), 'FY 23-24')
        self.assertEqual(str(AnnualReport(year=2024)), 'Annual Report 2024 (2024)')

    def test_public_url_prefers_uploaded_pdf(self):
        report = AnnualReport.objects.create(year=2023, pdf_file=file_upload('r.pdf'), external_url='https://example.com/x')
        request = RequestFactory().get('/')
        self.assertTrue(report.get_public_url(request).startswith('http://testserver/'))
        self.assertTrue(report.get_public_url().startswith('/'))

    def test_public_url_falls_back_to_external(self):
        report = AnnualReport.objects.create(year=2022, external_url='https://example.com/x')
        self.assertEqual(report.get_public_url(), 'https://example.com/x')
        self.assertIsNone(AnnualReport(year=2021).get_public_url())

    def test_year_is_unique_and_ordered_descending(self):
        AnnualReport.objects.create(year=2020, external_url='https://e.com/a')
        AnnualReport.objects.create(year=2022, external_url='https://e.com/b')
        self.assertEqual([r.year for r in AnnualReport.objects.all()], [2022, 2020])
        with self.assertRaises(Exception):
            AnnualReport.objects.create(year=2020, external_url='https://e.com/c')


class MiscModelTests(TestCase):
    def test_pillar_pages_str(self):
        self.assertEqual(str(SanskarHomePage()), 'Sanskar home page')
        self.assertEqual(str(SwarajHomePage()), 'Swaraj home page')
        self.assertEqual(str(SwabalambanHomePage()), 'Swabalamban home page')

    def test_home_page_defaults(self):
        page = HomePage.objects.create(banner_image='tests/b.gif')
        self.assertEqual(page.visitors_count, 0)
        self.assertEqual(str(page), 'Bandhu Home Page Content')

    def test_designation_default_rank(self):
        self.assertEqual(Designation.objects.create(title='Core Team').rank, 9999)
