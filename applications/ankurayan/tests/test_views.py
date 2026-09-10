"""Regression tests for applications.ankurayan.views."""

import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from bandhuapp.tests.support import (
    TempMediaMixin, file_upload, image_upload, make_admin, make_user,
)
from applications.ankurayan.models import (
    Activity, ActivityCategory, Ankurayan, AnkurayanInvitationLetter,
    AnkurayanPublicationFile, AnkurayanReportFile, Guest, HomePage,
    Participant, Photo,
)

AJAX = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}


def make_ankurayan(year=2024, **overrides):
    data = dict(
        year=year, title=f'Ankurayan {year}', theme='Theme', description='Desc',
        start_date=date(year, 12, 17), end_date=date(year, 12, 19),
        logo=image_upload('logo.gif'), slug=str(year),
    )
    data.update(overrides)
    return Ankurayan.objects.create(**data)


class AnkurayanViewTestBase(TempMediaMixin, TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.member = make_user()
        self.ankurayan = make_ankurayan()
        self.detail_url = reverse('ankurayan:AnkurayanDetail', kwargs={'slug': '2024'})

    def login_admin(self):
        self.client.force_login(self.admin)


class IndexAndDetailTests(AnkurayanViewTestBase):
    def test_index_lists_years_newest_first(self):
        make_ankurayan(2020)
        HomePage.objects.create(tagline='Tag', description='Home desc')
        response = self.client.get('/ankurayan/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([a.year for a in response.context['ankurayans']], [2024, 2020])
        self.assertEqual(response.context['content'].tagline, 'Tag')

    def test_detail_unknown_slug_404(self):
        self.assertEqual(self.client.get('/ankurayan/detail/nope/').status_code, 404)

    def test_detail_public_context(self):
        other = make_ankurayan(2020)
        category = ActivityCategory.objects.create(ankurayan=self.ankurayan, name='Art')
        ActivityCategory.objects.create(ankurayan=self.ankurayan, name='Empty')
        activity = Activity.objects.create(
            category=category, name='Painting', description='d', date=date(2024, 12, 17))
        approved = Photo.objects.create(
            ankurayan=self.ankurayan, picture=image_upload('a.gif'), activity=activity, approved=True)
        pending = Photo.objects.create(
            ankurayan=self.ankurayan, picture=image_upload('b.gif'), approved=False)
        Participant.objects.create(
            ankurayan=self.ankurayan, name='Kid', school_class='5', address='x', contact_no='1')
        Guest.objects.create(ankurayan=self.ankurayan, name='G', profession='P')
        AnkurayanReportFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='R')
        AnkurayanPublicationFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='P')
        AnkurayanInvitationLetter.objects.create(ankurayan=self.ankurayan, file=file_upload('inv.pdf'))

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertFalse(ctx['check_admin'])
        self.assertEqual(list(ctx['categories']), [category])  # only categories with activities
        self.assertEqual(list(ctx['photos']), [approved])
        self.assertEqual(list(ctx['unapproved_photos']), [pending])
        self.assertEqual(list(ctx['ankurayans']), [other])
        self.assertEqual(len(ctx['activity_img']), 1)
        self.assertEqual(list(ctx['activity_img'][0]), [approved])
        self.assertEqual(ctx['participants'].count(), 1)
        self.assertEqual(ctx['guests'].count(), 1)
        self.assertEqual(ctx['report_files'].count(), 1)
        self.assertEqual(ctx['publication_files'].count(), 1)
        self.assertIsNotNone(ctx['invitation_letter'])
        self.assertFalse(ctx['open_signup_modal'])

    def test_detail_admin_signup_modal_and_prefill(self):
        self.login_admin()
        session = self.client.session
        session['signup_modal_prefill_email'] = 'new@example.com'
        session.save()
        response = self.client.get(self.detail_url + '?signup_modal=1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['check_admin'])
        self.assertTrue(response.context['open_signup_modal'])
        self.assertEqual(response.context['signup_form'].initial['email'], 'new@example.com')
        self.assertNotIn('signup_modal_prefill_email', self.client.session)


class CreateAnkurayanTests(AnkurayanViewTestBase):
    url = reverse('ankurayan:CreateAnkurayan')

    def test_anonymous_redirects_to_login(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_non_admin_redirected_to_index(self):
        self.client.force_login(self.member)
        response = self.client.post(self.url, {})
        self.assertRedirects(response, '/ankurayan/', fetch_redirect_response=False)

    def test_get_redirects_to_index(self):
        self.login_admin()
        self.assertRedirects(self.client.get(self.url), '/ankurayan/', fetch_redirect_response=False)

    def test_post_creates_and_redirects_to_detail(self):
        self.login_admin()
        response = self.client.post(self.url, {
            'year': '2025', 'title': 'Ankurayan 2025', 'theme': 'T', 'description': 'D',
            'start_date': '2025-12-17', 'end_date': '2025-12-19', 'logo': image_upload(),
        })
        self.assertRedirects(response, '/ankurayan/detail/2025/', fetch_redirect_response=False)
        created = Ankurayan.objects.get(year=2025)
        self.assertEqual(created.slug, '2025')
        self.assertTrue(created.logo.name.startswith('ankurayan/logo/'))

    def test_duplicate_year_rejected(self):
        self.login_admin()
        response = self.client.post(self.url, {
            'year': '2024', 'title': 'x', 'theme': 'x', 'description': 'x',
            'start_date': '2024-12-17', 'end_date': '2024-12-19', 'logo': image_upload(),
        }, follow=True)
        self.assertEqual(Ankurayan.objects.count(), 1)
        self.assertIn('already exists', [m.message for m in response.context['messages']][0])


class SectionUpdateTests(AnkurayanViewTestBase):
    def url(self):
        return reverse('ankurayan:UpdateAnkurayanSection', kwargs={'slug': '2024'})

    def test_requires_admin(self):
        self.client.force_login(self.member)
        response = self.client.post(self.url(), {'field': 'reports', 'content': 'x'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_get_redirects(self):
        self.login_admin()
        self.assertRedirects(self.client.get(self.url()), self.detail_url, fetch_redirect_response=False)

    def test_updates_each_allowed_field(self):
        self.login_admin()
        for field, fragment in (('description', 'modalDescription'), ('reports', 'modalReports'),
                                ('publications', 'modalPublications'), ('visitors', 'modalVisitors')):
            response = self.client.post(self.url(), {'field': field, 'content': f'new {field}'})
            self.assertEqual(response.url, self.detail_url + '#' + fragment)
            self.ankurayan.refresh_from_db()
            self.assertEqual(getattr(self.ankurayan, field), f'new {field}')

    def test_unknown_field_ignored(self):
        self.login_admin()
        response = self.client.post(self.url(), {'field': 'slug', 'content': 'hack'})
        self.assertEqual(response.url, self.detail_url)
        self.ankurayan.refresh_from_db()
        self.assertEqual(self.ankurayan.slug, '2024')


class ReportAndPublicationFileTests(AnkurayanViewTestBase):
    def test_upload_report(self):
        self.login_admin()
        url = reverse('ankurayan:UploadAnkurayanReport', kwargs={'slug': '2024'})
        self.assertRedirects(self.client.get(url), self.detail_url, fetch_redirect_response=False)
        response = self.client.post(url, {'report_file': file_upload('r.pdf'), 'title': ' Annual '})
        self.assertEqual(response.url, self.detail_url + '#modalReports')
        self.assertEqual(self.ankurayan.report_files.get().title, 'Annual')
        # Untitled upload falls back to filename
        self.client.post(url, {'report_file': file_upload('named.pdf')})
        self.assertTrue(AnkurayanReportFile.objects.filter(title='named.pdf').exists())
        # Missing file -> error message, nothing created
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(AnkurayanReportFile.objects.count(), 2)
        self.assertIn('Please select a file.', [m.message for m in response.context['messages']])

    def test_upload_publication(self):
        self.login_admin()
        url = reverse('ankurayan:UploadAnkurayanPublication', kwargs={'slug': '2024'})
        self.assertRedirects(self.client.get(url), self.detail_url, fetch_redirect_response=False)
        response = self.client.post(url, {'publication_file': file_upload('p.pdf'), 'title': 'Pub'})
        self.assertEqual(response.url, self.detail_url + '#modalPublications')
        self.assertEqual(self.ankurayan.publication_files.get().title, 'Pub')
        self.client.post(url, {'publication_file': file_upload('named.pdf')})
        self.assertTrue(AnkurayanPublicationFile.objects.filter(title='named.pdf').exists())
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(AnkurayanPublicationFile.objects.count(), 2)
        self.assertIn('Please select a file.', [m.message for m in response.context['messages']])

    def test_update_and_delete_report_file(self):
        self.login_admin()
        rf = AnkurayanReportFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='old')
        update_url = reverse('ankurayan:UpdateAnkurayanReportFile', kwargs={'pk': rf.pk})
        delete_url = reverse('ankurayan:DeleteAnkurayanReportFile', kwargs={'pk': rf.pk})
        self.assertRedirects(self.client.get(update_url), '/ankurayan/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get(delete_url), '/ankurayan/', fetch_redirect_response=False)
        response = self.client.post(update_url, {'title': ' renamed '})
        self.assertEqual(response.url, self.detail_url + '#modalReports')
        rf.refresh_from_db()
        self.assertEqual(rf.title, 'renamed')
        response = self.client.post(delete_url)
        self.assertEqual(response.url, self.detail_url + '#modalReports')
        self.assertFalse(AnkurayanReportFile.objects.filter(pk=rf.pk).exists())
        self.assertEqual(self.client.post(delete_url).status_code, 404)

    def test_update_and_delete_publication_file(self):
        self.login_admin()
        pf = AnkurayanPublicationFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='old')
        update_url = reverse('ankurayan:UpdateAnkurayanPublicationFile', kwargs={'pk': pf.pk})
        delete_url = reverse('ankurayan:DeleteAnkurayanPublicationFile', kwargs={'pk': pf.pk})
        self.assertRedirects(self.client.get(update_url), '/ankurayan/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get(delete_url), '/ankurayan/', fetch_redirect_response=False)
        response = self.client.post(update_url, {'title': 'renamed'})
        self.assertEqual(response.url, self.detail_url + '#modalPublications')
        pf.refresh_from_db()
        self.assertEqual(pf.title, 'renamed')
        response = self.client.post(delete_url)
        self.assertEqual(response.url, self.detail_url + '#modalPublications')
        self.assertFalse(AnkurayanPublicationFile.objects.filter(pk=pf.pk).exists())


class InvitationLetterTests(AnkurayanViewTestBase):
    def setUp(self):
        super().setUp()
        self.upload_url = reverse('ankurayan:UploadAnkurayanInvitation', kwargs={'slug': '2024'})
        self.delete_url = reverse('ankurayan:DeleteAnkurayanInvitation', kwargs={'slug': '2024'})
        self.login_admin()

    def test_get_redirects(self):
        self.assertRedirects(self.client.get(self.upload_url), self.detail_url, fetch_redirect_response=False)
        self.assertRedirects(self.client.get(self.delete_url), self.detail_url, fetch_redirect_response=False)

    def test_missing_file_errors(self):
        response = self.client.post(self.upload_url, {}, follow=True)
        self.assertFalse(AnkurayanInvitationLetter.objects.exists())
        self.assertIn('Please select a file.', [m.message for m in response.context['messages']])

    def test_upload_then_replace_then_delete(self):
        response = self.client.post(self.upload_url, {'invitation_file': file_upload('one.pdf')})
        self.assertEqual(response.url, self.detail_url + '#modalInvitationLetter')
        letter = AnkurayanInvitationLetter.objects.get(ankurayan=self.ankurayan)
        first_name = letter.file.name
        self.assertIn('one', first_name)

        self.client.post(self.upload_url, {'invitation_file': file_upload('two.pdf')})
        self.assertEqual(AnkurayanInvitationLetter.objects.count(), 1)
        letter.refresh_from_db()
        self.assertIn('two', letter.file.name)
        self.assertNotEqual(letter.file.name, first_name)

        response = self.client.post(self.delete_url)
        self.assertEqual(response.url, self.detail_url + '#modalInvitationLetter')
        self.assertFalse(AnkurayanInvitationLetter.objects.exists())
        # Deleting again is a no-op redirect
        self.assertEqual(self.client.post(self.delete_url).status_code, 302)


class ParticipantAndCategoryTests(AnkurayanViewTestBase):
    def test_add_participant(self):
        url = reverse('ankurayan:AddParticipant')
        self.login_admin()
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        response = self.client.post(url, {
            'slug': '2024', 'name': 'Kid', 'gender': 'F', 'school_class': '6',
            'contact_no': '123', 'address': 'Village',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        p = Participant.objects.get()
        self.assertEqual((p.ankurayan, p.gender, p.school_class), (self.ankurayan, 'F', '6'))
        self.assertEqual(self.client.post(url, {'slug': 'missing', 'name': 'x'}).status_code, 404)

    def test_add_activity_category(self):
        url = reverse('ankurayan:AddActivityCategory')
        self.login_admin()
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        response = self.client.post(url, {'slug': '2024', 'name': 'Music'})
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertTrue(ActivityCategory.objects.filter(ankurayan=self.ankurayan, name='Music').exists())

    def test_member_cannot_add(self):
        self.client.force_login(self.member)
        response = self.client.post(reverse('ankurayan:AddParticipant'), {'slug': '2024'})
        self.assertTrue(response.url.startswith('/accounts/login/'))
        self.assertEqual(Participant.objects.count(), 0)


class GuestTests(AnkurayanViewTestBase):
    def test_add_guest_defaults_and_validation(self):
        url = reverse('ankurayan:AddGuest')
        self.login_admin()
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        response = self.client.post(url, {
            'slug': '2024', 'name': 'Guest One', 'profession': 'Judge', 'about': 'About',
            'avatar': 'alien',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        guest = Guest.objects.get()
        self.assertEqual(guest.avatar, 'man')  # invalid avatar coerced
        self.assertEqual(guest.email, '')
        self.assertFalse(guest.photo)

        self.client.post(url, {
            'slug': '2024', 'name': 'Guest Two', 'profession': 'Official', 'about': 'A',
            'avatar': 'woman', 'email': 'g@example.com', 'contact_no': '99',
            'facebook_url': 'https://fb.example/x', 'linkedin_url': 'https://li.example/x',
            'photo': image_upload('g.gif'),
        })
        guest2 = Guest.objects.get(name='Guest Two')
        self.assertEqual(guest2.avatar, 'woman')
        self.assertEqual(guest2.email, 'g@example.com')
        self.assertTrue(guest2.photo.name.startswith('ankurayan/guests/'))
        self.assertEqual(self.client.post(url, {'slug': 'missing'}).status_code, 404)

    def _guest(self, **overrides):
        data = dict(ankurayan=self.ankurayan, name='G', profession='P', about='A', avatar='man')
        data.update(overrides)
        return Guest.objects.create(**data)

    def test_update_guest_get_redirects(self):
        guest = self._guest()
        self.login_admin()
        response = self.client.get(reverse('ankurayan:UpdateGuest', kwargs={'pk': guest.pk}))
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)

    def test_update_guest_validation_errors(self):
        guest = self._guest()
        self.login_admin()
        url = reverse('ankurayan:UpdateGuest', kwargs={'pk': guest.pk})
        cases = (
            ({'profession': 'P', 'about': 'A'}, 'Name is required.'),
            ({'name': 'N', 'about': 'A'}, 'Profession is required.'),
            ({'name': 'N', 'profession': 'P'}, 'About is required.'),
        )
        for data, err in cases:
            response = self.client.post(url, data, **AJAX)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(json.loads(response.content), {'success': False, 'error': err})
        # Non-AJAX error path -> message + redirect
        response = self.client.post(url, {'profession': 'P', 'about': 'A'}, follow=True)
        self.assertIn('Name is required.', [m.message for m in response.context['messages']])
        guest.refresh_from_db()
        self.assertEqual(guest.name, 'G')

    def test_update_guest_success_ajax_and_redirect(self):
        guest = self._guest()
        self.login_admin()
        url = reverse('ankurayan:UpdateGuest', kwargs={'pk': guest.pk})
        response = self.client.post(url, {
            'name': ' New ', 'profession': 'Prof', 'about': 'About', 'quote': 'Q',
            'facebook_url': 'https://fb.example/', 'linkedin_url': 'https://li.example/',
            'avatar': 'woman', 'photo': image_upload('p.gif'),
        }, **AJAX)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload['success'])
        self.assertEqual(payload['guest']['name'], 'New')
        self.assertEqual(payload['guest']['avatar'], 'woman')
        self.assertTrue(payload['guest']['photo_url'].startswith('/media/ankurayan/guests/'))
        guest.refresh_from_db()
        self.assertEqual((guest.quote, guest.facebook_url), ('Q', 'https://fb.example/'))

        # Plain form post: invalid avatar keeps the existing one, no photo -> unchanged
        response = self.client.post(url, {
            'name': 'N2', 'profession': 'P2', 'about': 'A2', 'avatar': 'robot',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        guest.refresh_from_db()
        self.assertEqual((guest.name, guest.avatar), ('N2', 'woman'))
        self.assertTrue(guest.photo)

    def test_update_guest_without_photo_reports_empty_url(self):
        guest = self._guest()
        self.login_admin()
        response = self.client.post(reverse('ankurayan:UpdateGuest', kwargs={'pk': guest.pk}),
                                    {'name': 'N', 'profession': 'P', 'about': 'A'}, **AJAX)
        self.assertEqual(json.loads(response.content)['guest']['photo_url'], '')

    def test_delete_guest(self):
        guest = self._guest()
        other = self._guest(name='Other')
        self.login_admin()
        url = reverse('ankurayan:DeleteGuest', kwargs={'pk': guest.pk})
        self.assertRedirects(self.client.get(url), self.detail_url, fetch_redirect_response=False)
        self.assertTrue(Guest.objects.filter(pk=guest.pk).exists())
        response = self.client.post(url, **AJAX)
        self.assertEqual(json.loads(response.content), {'success': True})
        self.assertFalse(Guest.objects.filter(pk=guest.pk).exists())
        response = self.client.post(reverse('ankurayan:DeleteGuest', kwargs={'pk': other.pk}), follow=True)
        self.assertIn('Guest removed.', [m.message for m in response.context['messages']])
        self.assertEqual(Guest.objects.count(), 0)
        self.assertEqual(self.client.post(url).status_code, 404)


class ActivityWinnersGalleryTests(AnkurayanViewTestBase):
    def setUp(self):
        super().setUp()
        self.category = ActivityCategory.objects.create(ankurayan=self.ankurayan, name='Art')
        self.login_admin()

    def test_create_activity_with_images(self):
        url = reverse('ankurayan:CreateActivity')
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        response = self.client.post(url, {
            'slug': '2024', 'activity_name': 'Painting', 'category': str(self.category.pk),
            'description': 'D', 'date': '2024-12-18',
            'activity_images': [image_upload('1.gif'), image_upload('2.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        activity = Activity.objects.get(name='Painting')
        self.assertEqual(activity.category, self.category)
        photos = Photo.objects.filter(activity=activity)
        self.assertEqual(photos.count(), 2)
        self.assertTrue(all(p.approved for p in photos))
        self.assertEqual(self.client.post(url, {
            'slug': '2024', 'activity_name': 'x', 'category': '999', 'description': 'D',
            'date': '2024-12-18'}).status_code, 404)

    def test_add_winners(self):
        url = reverse('ankurayan:AddWinners')
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        activity = Activity.objects.create(
            category=self.category, name='Quiz', description='d', date=date(2024, 12, 17))
        kids = [Participant.objects.create(
            ankurayan=self.ankurayan, name=f'K{i}', school_class='5', address='a', contact_no='1')
            for i in range(3)]
        response = self.client.post(url, {
            'slug': '2024', 'pk': str(activity.pk), 'activity_name': 'Quiz',
            'pk_winner': kids[0].pk, 'pk_runner_up1': kids[1].pk, 'pk_runner_up2': kids[2].pk,
            'activity_images': [image_upload('w.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        activity.refresh_from_db()
        self.assertEqual((activity.winner, activity.runner_up1, activity.runner_up2), tuple(kids))
        photo = Photo.objects.get(activity=activity)
        self.assertFalse(photo.approved)  # winners photos start unapproved
        self.assertEqual(self.client.post(url, {
            'slug': '2024', 'pk': activity.pk, 'pk_winner': 999,
            'pk_runner_up1': kids[1].pk, 'pk_runner_up2': kids[2].pk}).status_code, 404)

    def test_add_to_gallery_admin_photos_auto_approved(self):
        url = reverse('ankurayan:AddToGallery')
        self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False)
        response = self.client.post(url, {
            'slug': '2024', 'gallery_images': [image_upload('g1.gif'), image_upload('g2.gif')]})
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertEqual(Photo.objects.filter(ankurayan=self.ankurayan, approved=True).count(), 2)
        self.assertEqual(self.client.post(url, {'slug': 'missing'}).status_code, 404)


class AdminApprovalTests(AnkurayanViewTestBase):
    url = reverse('ankurayan:ImageAdminApproval')

    def setUp(self):
        super().setUp()
        self.login_admin()
        self.photo = Photo.objects.create(
            ankurayan=self.ankurayan, picture=image_upload('p.gif'), approved=False)

    def test_get_redirects_home(self):
        self.assertRedirects(self.client.get(self.url), '/', fetch_redirect_response=False)

    def test_approve_form_post_redirects(self):
        response = self.client.post(self.url, {
            'ankurayan': '2024', 'image': self.photo.pk, 'status': 'approve'})
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.photo.refresh_from_db()
        self.assertTrue(self.photo.approved)

    def test_approve_ajax_returns_serialized_photos(self):
        response = self.client.post(self.url, {
            'ankurayan': '2024', 'image': self.photo.pk, 'status': 'approve'}, **AJAX)
        self.assertEqual(response.status_code, 200)
        payload = json.loads(json.loads(response.content))
        self.assertEqual(len(payload), 1)
        self.assertTrue(payload[0]['fields']['approved'])

    def test_reject_deletes_photo_and_file(self):
        path = self.photo.picture.path
        response = self.client.post(self.url, {
            'ankurayan': '2024', 'image': self.photo.pk, 'status': 'reject'})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Photo.objects.filter(pk=self.photo.pk).exists())
        import os
        self.assertFalse(os.path.exists(path))

    def test_unknown_photo_404(self):
        response = self.client.post(self.url, {'ankurayan': '2024', 'image': 999, 'status': 'approve'})
        self.assertEqual(response.status_code, 404)

    def test_member_blocked(self):
        self.client.force_login(self.member)
        response = self.client.post(self.url, {
            'ankurayan': '2024', 'image': self.photo.pk, 'status': 'approve'})
        self.assertTrue(response.url.startswith('/accounts/login/'))
        self.photo.refresh_from_db()
        self.assertFalse(self.photo.approved)
