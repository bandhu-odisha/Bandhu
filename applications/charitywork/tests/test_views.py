"""Regression tests for the Other Activities (charitywork) views, models and admin."""

import json
from datetime import date

from django.contrib.admin.sites import site as admin_site
from django.test import TestCase
from django.urls import reverse

from applications.charitywork.models import Activity, Charity, HomePage, Photo, Volunteer
from bandhuapp.tests.support import (
    TempMediaMixin, image_upload, make_admin, make_profile, make_user,
)

LOGIN_URL = '/accounts/login/'


def make_charity(title='Relief Drive', purpose='Cyclone', location='Puri', slug='relief-drive'):
    return Charity.objects.create(
        title=title, purpose=purpose, location=location, slug=slug,
        description='Helping people after the storm.', image=image_upload('hero.gif'),
        start_date=date(2024, 1, 1), end_date=date(2024, 1, 5),
    )


class ModelTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.charity = make_charity()

    def test_str_methods(self):
        activity = Activity.objects.create(
            charity=self.charity, name='Food', description='d', date=date(2024, 1, 2),
        )
        volunteer = Volunteer.objects.create(
            charity=self.charity, name='Vol', email='v@example.com', contact_no='1',
        )
        photo = Photo.objects.create(charity=self.charity, picture=image_upload())
        homepage = HomePage.objects.create(tagline='t', description='d')
        self.assertEqual(str(self.charity), 'Relief Drive - Puri')
        self.assertEqual(str(activity), 'Food - Relief Drive ')
        self.assertEqual(str(volunteer), 'Vol - Relief Drive')
        self.assertEqual(str(photo), 'Relief Drive')
        self.assertEqual(str(homepage), 'Other Activities Home Page Content')

    def test_volunteer_save_copies_profile_details(self):
        profile = make_profile(make_user('p@example.com'), first_name='Asha', last_name='Das',
                               contact_no='12345')
        volunteer = Volunteer.objects.create(charity=self.charity, profile=profile)
        self.assertEqual(volunteer.name, 'Asha Das')
        self.assertEqual(volunteer.email, 'p@example.com')
        self.assertEqual(volunteer.contact_no, '12345')


class IndexAndDetailTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.charity = make_charity()
        self.detail_url = reverse('charitywork:CharityDetail', args=[self.charity.slug])

    def test_index_lists_charities_and_content(self):
        homepage = HomePage.objects.create(
            tagline='Tag', description='Desc', picture=image_upload('index.gif'),
        )
        response = self.client.get(reverse('charitywork:charity_work'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['charity_works']), [self.charity])
        self.assertEqual(response.context['content'], homepage)
        self.assertContains(response, 'Relief Drive')

    def test_index_without_content(self):
        response = self.client.get(reverse('charitywork:charity_work'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['content'])

    def test_detail_404(self):
        self.assertEqual(
            self.client.get(reverse('charitywork:CharityDetail', args=['nope'])).status_code, 404,
        )

    def test_detail_splits_photos_by_approval(self):
        approved = Photo.objects.create(
            charity=self.charity, picture=image_upload('ok.gif'), approved=True,
        )
        pending = Photo.objects.create(charity=self.charity, picture=image_upload('p.gif'))
        Activity.objects.create(
            charity=self.charity, name='Food', description='d', date=date(2024, 1, 2),
        )
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['photos']), [approved])
        self.assertEqual(list(response.context['unapproved_photos']), [pending])
        self.assertEqual(response.context['activities'].count(), 1)
        self.assertFalse(response.context['check_admin'])

    def test_detail_admin_flag(self):
        self.client.force_login(make_admin())
        response = self.client.get(self.detail_url)
        self.assertTrue(response.context['check_admin'])
        self.client.force_login(make_user())
        response = self.client.get(self.detail_url)
        self.assertFalse(response.context['check_admin'])


class LoginRequiredTests(TestCase):
    def test_anonymous_redirected_to_login(self):
        for name in ('AddVolunteers', 'CreateActivity', 'AddToGallery', 'CreateCharity',
                     'ImageAdminApprovalAshram'):
            response = self.client.post(reverse(f'charitywork:{name}'), {})
            self.assertEqual(response.status_code, 302, name)
            self.assertTrue(response['Location'].startswith(LOGIN_URL), name)

    def test_get_redirects_home_for_logged_in_member(self):
        self.client.force_login(make_user())
        for name in ('AddVolunteers', 'CreateActivity', 'ImageAdminApprovalAshram'):
            response = self.client.get(reverse(f'charitywork:{name}'))
            self.assertRedirects(response, '/', fetch_redirect_response=False, msg_prefix=name)
        response = self.client.get(reverse('charitywork:CreateCharity'))
        self.assertRedirects(response, reverse('charitywork:charity_work'),
                             fetch_redirect_response=False)

    def test_gallery_requires_admin(self):
        self.client.force_login(make_user())
        response = self.client.post(reverse('charitywork:AddToGallery'), {'slug': 'x'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(LOGIN_URL))
        self.client.force_login(make_admin())
        response = self.client.get(reverse('charitywork:AddToGallery'))
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class CreateCharityTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client.force_login(make_admin())
        self.url = reverse('charitywork:CreateCharity')

    def test_creates_and_redirects_to_detail(self):
        response = self.client.post(self.url, {
            'title': 'Blood Camp', 'purpose': 'Health', 'location': 'Cuttack City',
            'start_date': '2024-02-01', 'end_date': '2024-02-02', 'description': 'd',
            'image': image_upload(),
        })
        charity = Charity.objects.get(title='Blood Camp')
        self.assertEqual(charity.slug, 'blood-camp-health-cuttack-city')
        self.assertEqual(charity.start_date, date(2024, 2, 1))
        self.assertRedirects(response, reverse('charitywork:CharityDetail', args=[charity.slug]),
                             fetch_redirect_response=False)

    def test_duplicate_rejected_with_message(self):
        make_charity()
        response = self.client.post(self.url, {
            'title': 'Relief Drive', 'purpose': 'Cyclone', 'location': 'Puri',
            'description': 'd',
        }, follow=True)
        self.assertEqual(Charity.objects.count(), 1)
        self.assertRedirects(response, reverse('charitywork:charity_work'))
        self.assertIn('already exists', [m.message for m in response.context['messages']][0])


class DetailMutationTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.charity = make_charity()
        self.slug = self.charity.slug
        self.detail_url = f'/other_activities/detail/{self.slug}/'
        self.client.force_login(make_admin())

    def test_add_named_volunteer(self):
        response = self.client.post(reverse('charitywork:AddVolunteers'), {
            'slug': self.slug, 'name': 'Guest', 'email': 'g@example.com',
            'contact_no': '555', 'volunteers': '',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        volunteer = Volunteer.objects.get()
        self.assertEqual((volunteer.name, volunteer.email, volunteer.profile),
                         ('Guest', 'g@example.com', None))

    def test_add_volunteers_from_member_emails(self):
        profile = make_profile(make_user('m@example.com'), first_name='Mem', last_name='Ber')
        response = self.client.post(reverse('charitywork:AddVolunteers'), {
            'slug': self.slug, 'name': '', 'volunteers': 'm@example.com,unknown@example.com',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertEqual(Volunteer.objects.count(), 2)
        self.assertEqual(Volunteer.objects.get(profile=profile).name, 'Mem Ber')
        self.assertTrue(Volunteer.objects.filter(profile=None, name='').exists())

    def test_add_volunteers_unknown_charity_404(self):
        response = self.client.post(reverse('charitywork:AddVolunteers'), {
            'slug': 'nope', 'name': 'x', 'volunteers': '',
        })
        self.assertEqual(response.status_code, 404)

    def test_create_activity_with_photos(self):
        response = self.client.post(reverse('charitywork:CreateActivity'), {
            'slug': self.slug, 'activity_name': 'Food supply', 'description': 'd',
            'date': '2024-01-03',
            'activity_images': [image_upload('a.gif'), image_upload('b.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        activity = Activity.objects.get(name='Food supply')
        self.assertEqual(activity.date, date(2024, 1, 3))
        photos = Photo.objects.filter(activity=activity, charity=self.charity)
        self.assertEqual(photos.count(), 2)
        self.assertTrue(all(p.approved for p in photos))

    def test_admin_gallery_upload_is_approved(self):
        response = self.client.post(reverse('charitywork:AddToGallery'), {
            'slug': self.slug, 'gallery_images': [image_upload('g.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertTrue(Photo.objects.get(charity=self.charity).approved)

    def test_admin_approval_approve_and_reject(self):
        url = reverse('charitywork:ImageAdminApprovalAshram')
        photo = Photo.objects.create(charity=self.charity, picture=image_upload('p.gif'))
        response = self.client.post(url, {
            'charity': self.slug, 'image': photo.pk, 'status': 'approve',
        })
        self.assertEqual(response.status_code, 200)
        photo.refresh_from_db()
        self.assertTrue(photo.approved)
        payload = json.loads(response.json())
        self.assertEqual(len(payload), 1)
        self.assertTrue(payload[0]['fields']['approved'])

        response = self.client.post(url, {
            'charity': self.slug, 'image': photo.pk, 'status': 'reject',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.json()), [])
        self.assertFalse(Photo.objects.filter(pk=photo.pk).exists())

    def test_admin_approval_unknown_photo_404(self):
        response = self.client.post(reverse('charitywork:ImageAdminApprovalAshram'), {
            'charity': self.slug, 'image': 999, 'status': 'approve',
        })
        self.assertEqual(response.status_code, 404)


class AdminSiteTests(TempMediaMixin, TestCase):
    def setUp(self):
        make_charity()
        self.client.force_login(make_admin())

    def test_changelists_render(self):
        for model in (Charity, Volunteer, Activity, Photo, HomePage):
            url = reverse(f'admin:charitywork_{model._meta.model_name}_changelist')
            self.assertEqual(self.client.get(url).status_code, 200, model)
        self.assertIn(Charity, admin_site._registry)

    def _add_data(self, slug):
        return {
            'title': 'Admin Camp', 'purpose': 'Health', 'location': 'Puri', 'slug': slug,
            'start_date': '2024-01-01', 'end_date': '2024-01-02', 'description': 'd',
            'image': image_upload('h.gif'), 'image_caption_en': '', 'image_caption_or': '',
        }

    def test_response_add_redirects_to_detail_when_next_given(self):
        url = reverse('admin:charitywork_charity_add') + '?next=activity_details'
        response = self.client.post(url, self._add_data('admin-camp'))
        self.assertRedirects(response, reverse('charitywork:CharityDetail', args=['admin-camp']),
                             fetch_redirect_response=False)
        self.assertTrue(Charity.objects.filter(slug='admin-camp').exists())

    def test_response_add_default_without_next(self):
        response = self.client.post(reverse('admin:charitywork_charity_add'),
                                    self._add_data('admin-camp-2'))
        self.assertRedirects(response, reverse('admin:charitywork_charity_changelist'),
                             fetch_redirect_response=False)
