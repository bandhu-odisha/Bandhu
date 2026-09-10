"""Model behaviour in bandhuapp/models.py not covered by the view-level suites."""

from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from bandhuapp.models import (
    AboutSlide,
    AboutUs,
    AnnualReport,
    Contact,
    CurrentUpdates,
    Designation,
    DesignationRole,
    Gallery,
    HeroSlide,
    HomeVisitor,
    PeoplesDesignation,
    Photo,
    RecentActivity,
    SanskarHomePage,
    SanskarHomePhoto,
    Staff,
    SwabalambanHomePage,
    SwabalambanHomePhoto,
    SwarajHomePage,
    SwarajHomePhoto,
    UrlData,
    Volunteer,
)
from bandhuapp.tests.support import TempMediaMixin, file_upload, make_profile, make_user


class RecentActivityTests(TempMediaMixin, TestCase):
    def test_str_and_default_link_hash(self):
        notice = RecentActivity.objects.create(title='Camp', description='d', start_date=date(2024, 1, 5))
        self.assertEqual(str(notice), 'Camp - 2024-01-05')
        notice.refresh_from_db()
        self.assertEqual(notice.link, '#')

    def test_uploaded_notice_file_overrides_link(self):
        notice = RecentActivity.objects.create(title='PDF', description='d', notice_file=file_upload('n.pdf'), link='x')
        notice.refresh_from_db()
        self.assertTrue(notice.link.startswith('/media/notice_files/'))

    def test_explicit_link_is_kept(self):
        notice = RecentActivity.objects.create(title='Link', description='d', link='https://example.com')
        notice.refresh_from_db()
        self.assertEqual(notice.link, 'https://example.com')

    def test_end_before_start_is_rejected(self):
        with self.assertRaises(ValueError):
            RecentActivity.objects.create(title='Bad', description='d', start_date=date(2024, 2, 1), end_date=date(2024, 1, 1))


class StrRepresentationTests(TestCase):
    def test_simple_model_strs(self):
        self.assertEqual(str(Photo(id=7)), 'Photo7')
        self.assertEqual(str(AboutUs()), 'About Us section text')
        self.assertEqual(str(AboutSlide(caption='A long caption')), 'A long caption')
        self.assertEqual(str(AboutSlide(pk=3)), 'About slide 3')
        self.assertEqual(str(SanskarHomePhoto(pk=1)), 'Sanskar photo 1')
        self.assertEqual(str(SwarajHomePhoto(pk=2)), 'Swaraj photo 2')
        self.assertEqual(str(SwabalambanHomePhoto(pk=3)), 'Swabalamban photo 3')
        self.assertEqual(str(HeroSlide(title='Hero')), 'Hero')
        self.assertEqual(str(HeroSlide(pk=4, title='')), 'Hero slide 4')
        self.assertEqual(str(HomeVisitor(name='Visitor')), 'Visitor')
        self.assertEqual(str(UrlData(url='https://e.com', hash='abc')), 'https://e.com to abc')
        self.assertEqual(str(CurrentUpdates(desc='x')), 'CurrentUpdates object (None)')

    def test_singleton_section_strs(self):
        volunteer = Volunteer(title='Join', tagline='t')
        gallery = Gallery(tagline='g')
        contact = Contact(address='a', contact_no='1', email='e@e.com')
        for obj in (volunteer, gallery, contact):
            self.assertIsInstance(str(obj), str)
            self.assertTrue(str(obj))

    def test_url_data_gets_generated_hash(self):
        row = UrlData.objects.create(url='https://example.com/x')
        self.assertTrue(row.hash)
        self.assertEqual(row.times_followed, 0)


class DesignationTests(TestCase):
    def test_designation_title_is_proper_cased_and_ordered_by_rank(self):
        low = Designation.objects.create(title='office bearers', rank=2)
        top = Designation.objects.create(title='core TEAM', rank=1)
        self.assertEqual(low.title, 'Office Bearers')
        self.assertEqual(str(top), '1 - Core Team')
        self.assertEqual(list(Designation.objects.all()), [top, low])

    def test_role_title_is_proper_cased_and_unique_per_designation(self):
        designation = Designation.objects.create(title='Office Bearers', rank=2)
        role = DesignationRole.objects.create(designation=designation, title='president', rank=1)
        self.assertEqual(role.title, 'President')
        self.assertEqual(str(role), 'Office Bearers: President')
        with self.assertRaises(Exception):
            DesignationRole.objects.create(designation=designation, title='President')


class PeoplesDesignationTests(TestCase):
    def setUp(self):
        self.profile = make_profile(make_user('staff@example.com'), first_name='Asha', last_name='Rao', profession='teacher')
        self.staff = Staff.objects.create(profile=self.profile, about='About Asha')
        self.core = Designation.objects.create(title='Core Team', rank=1)
        self.bearers = Designation.objects.create(title='Office Bearers', rank=2)
        self.other = Designation.objects.create(title='Other', rank=3)
        self.president = DesignationRole.objects.create(designation=self.bearers, title='President', rank=1)

    def test_staff_str(self):
        self.assertIn('Asha Rao', str(self.staff))

    def test_office_bearer_requires_role_and_role_must_match_designation(self):
        pd = PeoplesDesignation(staff=self.staff, designation=self.bearers)
        with self.assertRaises(ValidationError):
            pd.clean()
        PeoplesDesignation(staff=self.staff, designation=self.other).clean  # "Other" also needs a role
        with self.assertRaises(ValidationError):
            PeoplesDesignation(staff=self.staff, designation=self.other).clean()
        with self.assertRaises(ValidationError):
            PeoplesDesignation(staff=self.staff, designation=self.core, role=self.president).clean()
        PeoplesDesignation(staff=self.staff, designation=self.bearers, role=self.president).clean()
        PeoplesDesignation(staff=self.staff).clean()  # no designation yet: nothing to validate

    def test_core_team_rejects_role_and_duplicates(self):
        first = PeoplesDesignation.objects.create(staff=self.staff, designation=self.core)
        first.clean()  # editing the existing row is fine
        with self.assertRaises(ValidationError):
            PeoplesDesignation(staff=self.staff, designation=self.core, role=self.president).clean()
        with self.assertRaises(ValidationError):
            PeoplesDesignation(staff=self.staff, designation=self.core).clean()

    def test_str_and_desc_proper_case(self):
        pd = PeoplesDesignation.objects.create(
            staff=self.staff, designation=self.bearers, role=self.president, desc='  retired ENGINEER ',
        )
        self.assertEqual(pd.desc, 'Retired Engineer')
        self.assertEqual(str(pd), 'Asha Rao — Office Bearers (President)')
        core = PeoplesDesignation.objects.create(staff=self.staff, designation=self.core)
        self.assertEqual(str(core), 'Asha Rao — Core Team')

    def test_display_lines(self):
        bearer = PeoplesDesignation.objects.create(staff=self.staff, designation=self.bearers, role=self.president)
        self.assertEqual(bearer.display_lines, ['President', 'Teacher'])
        bearer.desc = 'Farmer'
        self.assertEqual(bearer.display_lines, ['President', 'Farmer'])

        core = PeoplesDesignation.objects.create(staff=self.staff, designation=self.core)
        self.assertEqual(core.display_lines, ['Teacher'])

        plain = PeoplesDesignation(staff=self.staff, designation=self.other)
        self.assertEqual(plain.display_lines, ['Teacher'])
        plain.desc = 'volunteer'
        self.assertEqual(plain.display_lines, ['Volunteer'])
        self.profile.profession = ''
        self.profile.save()
        self.assertEqual(PeoplesDesignation(designation=self.other).display_lines, [''])


class AnnualReportEdgeTests(TestCase):
    def test_unsaved_pdf_field_without_name_falls_back(self):
        report = AnnualReport(year=2024, external_url='https://e.com/r')
        report.pdf_file = None
        self.assertEqual(report.get_public_url(), 'https://e.com/r')


class PillarPageStrTests(TestCase):
    def test_pages(self):
        self.assertEqual(str(SanskarHomePage()), 'Sanskar home page')
        self.assertEqual(str(SwarajHomePage()), 'Swaraj home page')
        self.assertEqual(str(SwabalambanHomePage()), 'Swabalamban home page')
