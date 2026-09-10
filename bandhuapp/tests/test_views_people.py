"""People page, staff profiles, staff experiences and the external-link redirect."""

import unittest
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.contrib.auth.models import AnonymousUser

from bandhuapp import views
from bandhuapp.models import (
    Designation, DesignationRole, PeoplesDesignation, Staff, StaffExperience,
    StaffExperiencePhoto, UrlData,
)
from bandhuapp.tests.support import (
    TINY_GIF, TempMediaMixin, image_upload, make_admin, make_profile, make_user,
)


def make_staff(email='staff@example.com', first_name='Asha', last_name='Das', profession='Teacher', **staff_fields):
    user = make_user(email)
    profile = make_profile(user, first_name=first_name, last_name=last_name, profession=profession)
    fields = dict(about='About this person.')
    fields.update(staff_fields)
    return Staff.objects.create(profile=profile, **fields)


def assign(staff, title, rank=1, role_title=None, desc='', d_rank=None):
    designation, _ = Designation.objects.get_or_create(title=title, defaults={'rank': d_rank or rank})
    role = None
    if role_title:
        role, _ = DesignationRole.objects.get_or_create(designation=designation, title=role_title)
    return PeoplesDesignation.objects.create(staff=staff, designation=designation, role=role, desc=desc, rank=rank)


class HelperFunctionTests(TestCase):
    def test_safe_login_next(self):
        self.assertEqual(views._safe_login_next(None), '/')
        self.assertEqual(views._safe_login_next(123), '/')
        self.assertEqual(views._safe_login_next('  /people/ '), '/people/')
        self.assertEqual(views._safe_login_next('//evil.example'), '/')
        self.assertEqual(views._safe_login_next('https://evil.example'), '/')
        self.assertEqual(views._safe_login_next('/accounts/login/?next=/x'), '/')

    def test_must_complete_member_profile(self):
        self.assertFalse(views._must_complete_member_profile(AnonymousUser()))
        self.assertFalse(views._must_complete_member_profile(make_admin()))
        staff_user = make_user('s@example.com', is_staff=True)
        self.assertFalse(views._must_complete_member_profile(staff_user))
        member = make_user()
        self.assertTrue(views._must_complete_member_profile(member))
        make_profile(member)
        self.assertFalse(views._must_complete_member_profile(member))

    def test_can_manage_staff_experiences(self):
        staff = make_staff()
        self.assertFalse(views._can_manage_staff_experiences(AnonymousUser(), staff))
        self.assertTrue(views._can_manage_staff_experiences(make_admin(), staff))
        self.assertTrue(views._can_manage_staff_experiences(make_user('st@example.com', is_staff=True)))
        self.assertTrue(views._can_manage_staff_experiences(staff.profile.user, staff))
        other = make_user('other@example.com')
        self.assertFalse(views._can_manage_staff_experiences(other, staff))
        self.assertFalse(views._can_manage_staff_experiences(other, None))

    def test_people_back_url_infers_tab_from_designations(self):
        factory = RequestFactory()
        staff = make_staff()
        core = assign(staff, 'Core Team')
        req = factory.get('/people/x/')
        self.assertEqual(views._people_back_url(req, [core]), '/people/#core-team')
        office = assign(staff, 'Office Bearers', role_title='President')
        other = assign(staff, 'Other', role_title='Advisor')
        self.assertEqual(views._people_back_url(req, [office, other]), '/people/#office-bearers')
        self.assertEqual(views._people_back_url(req, [core, office]), '/people/#all')
        self.assertEqual(views._people_back_url(req, None), '/people/#all')
        explicit = factory.get('/people/x/?from=Core Team')
        self.assertEqual(views._people_back_url(explicit, [office]), '/people/#core-team')
        bogus = factory.get('/people/x/?from=nope')
        self.assertEqual(views._people_back_url(bogus, [core]), '/people/#core-team')


class PeoplePageTests(TestCase):
    def test_empty_people_page(self):
        response = self.client.get('/people/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['data'].keys()), ['All'])
        self.assertEqual(response.context['page_title'], 'People')

    # Regression: views.people() used to read `card.staff_id` on the SimpleNamespace built
    # by people_card_from_assignments(), which exposes `.staff` (a Staff instance) and no
    # `.staff_id`. That raised AttributeError -> HTTP 500 whenever both "Office Bearers"
    # and "Other" tabs were populated in one request. Fixed to `card.staff.id`.
    def test_tabs_ordered_and_office_bearers_merged_with_other(self):
        core = make_staff('core@example.com', 'Core', 'Person')
        officer = make_staff('officer@example.com', 'Office', 'Person', profession='Lawyer')
        both = make_staff('both@example.com', 'Both', 'Person')
        assign(core, 'Core Team', d_rank=2)
        assign(officer, 'Office Bearers', role_title='President', d_rank=1)
        assign(both, 'Office Bearers', role_title='Secretary', d_rank=1)
        assign(both, 'Other', role_title='Advisor', d_rank=3)
        assign(core, 'Volunteers', d_rank=5)

        response = self.client.get('/people/')
        data = response.context['data']
        self.assertEqual(list(data.keys()), ['All', 'Core Team', 'Office Bearers', 'Volunteers'])
        self.assertNotIn('Other', data)
        self.assertEqual(len(data['All']), 3)
        self.assertEqual({c.staff.id for c in data['Office Bearers']}, {officer.id, both.id})
        self.assertEqual(len(data['Office Bearers']), 2)  # `both` appears once despite two roles
        self.assertEqual([c.staff.id for c in data['Core Team']], [core.id])

    def test_other_without_office_bearers_is_relabelled(self):
        staff = make_staff()
        assign(staff, 'Other', role_title='Advisor')
        data = self.client.get('/people/').context['data']
        self.assertIn('Office Bearers', data)
        self.assertNotIn('Other', data)

    def test_same_staff_twice_in_one_tab_is_listed_once(self):
        staff = make_staff()
        assign(staff, 'Office Bearers', role_title='President', rank=1)
        assign(staff, 'Office Bearers', role_title='Treasurer', rank=2)
        data = self.client.get('/people/').context['data']
        self.assertEqual(len(data['Office Bearers']), 1)
        self.assertEqual(len(data['All']), 1)

    @unittest.expectedFailure
    def test_post_to_people_page_returns_a_response(self):
        """bandhuapp/views.py:760 `people` only handles GET; any other method returns None,
        so Django raises ValueError ("didn't return an HttpResponse") -> HTTP 500."""
        response = self.client.post('/people/')
        self.assertIn(response.status_code, (302, 405))


class StaffProfileTests(TestCase):
    def test_office_bearer_with_role_uses_role_title_and_desc(self):
        staff = make_staff(profession='Advocate')
        assign(staff, 'Office Bearers', role_title='President', desc='runs the trust', rank=1)
        assign(staff, 'Other', role_title='Advisor', rank=2, d_rank=3)
        response = self.client.get(f'/people/{staff.id}/')
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertTrue(ctx['is_office_bearer'])
        self.assertEqual(ctx['staff_position'], 'President · Advisor')
        self.assertEqual(ctx['staff_occupation'], 'Runs The Trust')
        self.assertEqual(ctx['designation_titles'], ['Office Bearers', 'Other'])
        self.assertEqual(ctx['primary_designation'].role.title, 'President')
        self.assertEqual(ctx['designation_desc'], 'Runs The Trust')
        self.assertFalse(ctx['can_manage_staff_experiences'])
        self.assertEqual(ctx['people_back_url'], '/people/#office-bearers')

    def test_office_bearer_with_role_but_no_desc_falls_back_to_profession(self):
        staff = make_staff(profession='Advocate')
        assign(staff, 'Office Bearers', role_title='President')
        ctx = self.client.get(f'/people/{staff.id}/').context
        self.assertEqual(ctx['staff_occupation'], 'Advocate')

    def test_office_bearer_without_role_splits_profession(self):
        staff = make_staff(profession='Secretary, Retired Teacher')
        assign(staff, 'Office Bearers')  # legacy row without a role
        ctx = self.client.get(f'/people/{staff.id}/').context
        self.assertTrue(ctx['is_office_bearer'])
        self.assertEqual(ctx['staff_position'], 'Secretary')
        self.assertEqual(ctx['staff_occupation'], 'Retired Teacher')

    def test_core_team_member_has_no_position(self):
        staff = make_staff(profession='Engineer')
        assign(staff, 'Core Team')
        ctx = self.client.get(f'/people/{staff.id}/?from=core-team').context
        self.assertFalse(ctx['is_office_bearer'])
        self.assertEqual(ctx['staff_position'], '')
        self.assertEqual(ctx['staff_occupation'], 'Engineer')
        self.assertIsNone(ctx['primary_designation'].role)
        self.assertEqual(ctx['people_back_url'], '/people/#core-team')

    def test_staff_without_designations(self):
        staff = make_staff()
        ctx = self.client.get(f'/people/{staff.id}/').context
        self.assertIsNone(ctx['primary_designation'])
        self.assertEqual(ctx['designation_titles'], [])
        self.assertEqual(ctx['people_back_url'], '/people/#all')

    def test_owner_and_admin_can_manage_experiences(self):
        staff = make_staff()
        StaffExperience.objects.create(staff=staff, message='Great time')
        self.client.force_login(staff.profile.user)
        response = self.client.get(f'/people/{staff.id}/')
        self.assertTrue(response.context['can_manage_staff_experiences'])
        self.assertEqual(list(response.context['experiences']), list(staff.experiences.all()))
        self.client.force_login(make_admin())
        self.assertTrue(self.client.get(f'/people/{staff.id}/').context['can_manage_staff_experiences'])

    @unittest.expectedFailure
    def test_unknown_staff_id_is_404(self):
        """bandhuapp/views.py:809-817 uses `.get(id=id)` without get_object_or_404, so an
        unknown id raises Staff.DoesNotExist (HTTP 500) instead of 404."""
        self.assertEqual(self.client.get('/people/999999/').status_code, 404)

    @unittest.expectedFailure
    def test_post_to_staff_profile_returns_a_response(self):
        """bandhuapp/views.py:807 `staff_profile` returns None for non-GET methods (HTTP 500)."""
        staff = make_staff()
        self.assertIn(self.client.post(f'/people/{staff.id}/').status_code, (302, 405))


class StaffExperiencesPageTests(TestCase):
    def test_lists_experiences(self):
        staff = make_staff()
        exp = StaffExperience.objects.create(staff=staff, message='Hello')
        response = self.client.get(f'/people/{staff.id}/experiences/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['staff'], staff)
        self.assertEqual(list(response.context['experiences']), [exp])

    def test_unknown_staff_is_404(self):
        self.assertEqual(self.client.get('/people/999999/experiences/').status_code, 404)


class ShareExperienceTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.staff = make_staff()
        self.url = f'/people/{self.staff.id}/share-experience/'

    def test_anonymous_is_denied(self):
        response = self.client.post(self.url, {'experience': 'x'})
        self.assertRedirects(response, f'/people/{self.staff.id}/', fetch_redirect_response=False)
        self.assertEqual(StaffExperience.objects.count(), 0)

    def test_other_member_is_denied(self):
        self.client.force_login(make_user('other@example.com'))
        self.client.post(self.url, {'experience': 'x'})
        self.assertEqual(StaffExperience.objects.count(), 0)

    def test_get_redirects_to_profile(self):
        self.client.force_login(self.staff.profile.user)
        self.assertRedirects(self.client.get(self.url), f'/people/{self.staff.id}/', fetch_redirect_response=False)

    def test_owner_shares_with_photos(self):
        self.client.force_login(self.staff.profile.user)
        not_image = SimpleUploadedFile('notes.txt', b'hi', content_type='text/plain')
        response = self.client.post(self.url, {
            'experience': '  A memorable year  ',
            'photos_captions': ['first day', ''],
            'photos': [image_upload('a.gif'), not_image, image_upload('c.gif')],
        })
        self.assertRedirects(
            response, f'/people/{self.staff.id}/#experiences-heading', fetch_redirect_response=False)
        exp = StaffExperience.objects.get()
        self.assertEqual(exp.message, 'A memorable year')
        photos = list(exp.photos.order_by('id'))
        self.assertEqual(len(photos), 2)  # text/plain upload skipped
        self.assertEqual(photos[0].caption, 'First Day')
        self.assertEqual(photos[1].caption, '')

    def test_empty_message_is_rejected(self):
        self.client.force_login(make_admin())
        response = self.client.post(self.url, {'experience': '   '}, follow=True)
        self.assertEqual(StaffExperience.objects.count(), 0)
        self.assertContains(response, 'Please add your experience')


class EditExperienceTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.staff = make_staff()
        self.exp = StaffExperience.objects.create(staff=self.staff, message='Original')
        self.photo = StaffExperiencePhoto.objects.create(
            experience=self.exp, image=image_upload('old.gif'), caption='Old')
        self.url = f'/people/{self.staff.id}/experience/{self.exp.id}/edit/'

    def test_get_redirects(self):
        self.assertRedirects(self.client.get(self.url), f'/people/{self.staff.id}/', fetch_redirect_response=False)

    def test_non_owner_denied(self):
        self.client.force_login(make_user('other@example.com'))
        self.client.post(self.url, {'experience': 'Changed'})
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.message, 'Original')

    def test_experience_must_belong_to_staff(self):
        other = make_staff('o@example.com', 'Other', 'Staff')
        self.client.force_login(make_admin())
        response = self.client.post(
            f'/people/{other.id}/experience/{self.exp.id}/edit/', {'experience': 'Changed'})
        self.assertEqual(response.status_code, 404)

    def test_owner_updates_message_captions_and_photos(self):
        keep = StaffExperiencePhoto.objects.create(
            experience=self.exp, image=image_upload('keep.gif'), caption='Keep')
        self.client.force_login(self.staff.profile.user)
        response = self.client.post(self.url, {
            'experience': 'Updated text',
            'photos_to_remove': [str(self.photo.id), 'not-an-int', '999999'],
            f'caption_{keep.id}': 'new caption',
            'photos_captions': ['added one'],
            'photos': [image_upload('new.gif')],
        })
        self.assertRedirects(response, f'/people/{self.staff.id}/', fetch_redirect_response=False)
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.message, 'Updated text')
        self.assertFalse(StaffExperiencePhoto.objects.filter(id=self.photo.id).exists())
        keep.refresh_from_db()
        self.assertEqual(keep.caption, 'New Caption')
        captions = sorted(self.exp.photos.values_list('caption', flat=True))
        self.assertEqual(captions, ['Added One', 'New Caption'])

    def test_blank_caption_clears_existing_caption(self):
        self.client.force_login(make_admin())
        self.client.post(self.url, {'experience': 'Still here', f'caption_{self.photo.id}': ''})
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.caption, '')

    def test_empty_message_keeps_original(self):
        self.client.force_login(make_admin())
        response = self.client.post(self.url, {'experience': ''}, follow=True)
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.message, 'Original')
        self.assertContains(response, 'Message cannot be empty')


class DeleteExperienceTests(TestCase):
    def setUp(self):
        self.staff = make_staff()
        self.exp = StaffExperience.objects.create(staff=self.staff, message='Bye')
        self.url = f'/people/{self.staff.id}/experience/{self.exp.id}/delete/'

    def test_get_redirects_without_deleting(self):
        self.client.force_login(make_admin())
        self.client.get(self.url)
        self.assertTrue(StaffExperience.objects.filter(id=self.exp.id).exists())

    def test_non_owner_denied(self):
        self.client.force_login(make_user('other@example.com'))
        response = self.client.post(self.url)
        self.assertRedirects(response, f'/people/{self.staff.id}/', fetch_redirect_response=False)
        self.assertTrue(StaffExperience.objects.filter(id=self.exp.id).exists())

    def test_owner_deletes(self):
        self.client.force_login(self.staff.profile.user)
        response = self.client.post(self.url, follow=True)
        self.assertFalse(StaffExperience.objects.filter(id=self.exp.id).exists())
        self.assertContains(response, 'Experience deleted')

    def test_wrong_staff_is_404(self):
        other = make_staff('o@example.com', 'Other', 'Staff')
        self.client.force_login(make_admin())
        self.assertEqual(
            self.client.post(f'/people/{other.id}/experience/{self.exp.id}/delete/').status_code, 404)


class ExternalLinkTests(TestCase):
    def test_follows_and_counts(self):
        link = UrlData.objects.create(url='https://example.org/doc')
        response = self.client.get(f'/links/{link.hash}')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], 'https://example.org/doc')
        link.refresh_from_db()
        self.assertEqual(link.times_followed, 1)

    def test_unknown_hash_goes_home(self):
        self.assertRedirects(self.client.get('/links/nope'), '/', fetch_redirect_response=False)

    def test_post_goes_home(self):
        link = UrlData.objects.create(url='https://example.org/doc')
        self.assertRedirects(self.client.post(f'/links/{link.hash}'), '/', fetch_redirect_response=False)
        link.refresh_from_db()
        self.assertEqual(link.times_followed, 0)
