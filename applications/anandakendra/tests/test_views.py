"""Regression tests for the Anandakendra views, models and admin."""

import json
import os
import unittest

from django.contrib.admin.sites import site as admin_site
from django.test import TestCase
from django.urls import reverse

from applications.anandakendra import admin as kendra_admin
from applications.anandakendra.models import (
    Acharya, Activity, ActivityCategory, AnandaKendra, Event, HomePage, Photo, Student,
)
from applications.anandakendra.views import _kendra_hero_locality_css
from bandhuapp.tests.support import (
    TempMediaMixin, image_upload, make_admin, make_profile, make_user,
)

LOGIN_URL = '/accounts/login/'


def make_kendra(name='Kendra One', locality='Cuttack', slug='kendra-one-cuttack'):
    return AnandaKendra.objects.create(
        name=name,
        locality=locality,
        slug=slug,
        description='A kendra description that is long enough to render.',
        address='Cuttack, Odisha',
        image=image_upload('hero.gif'),
    )


class HelperTests(TestCase):
    def test_locality_css_escapes_and_uses_nbsp(self):
        self.assertEqual(_kendra_hero_locality_css(None), '')
        self.assertEqual(
            _kendra_hero_locality_css('Say "hi" \\ there'),
            'Say\\0000a0 \\"hi\\"\\0000a0 \\\\\\0000a0 there',
        )


class ModelTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.kendra = make_kendra()

    def test_str_methods(self):
        category = ActivityCategory.objects.create(kendra=self.kendra, name='Yoga')
        activity = Activity.objects.create(
            category=category, name='Morning yoga', description='d', activity_time='6am',
        )
        student = Student.objects.create(
            kendra=self.kendra, name='Ravi', guardian_name='G', school_class='5',
            contact_no='1', address='a',
        )
        event = Event.objects.create(
            kendra=self.kendra, name='Annual day', description='d', date='2024-01-01',
            thumb=image_upload('thumb.gif'),
        )
        profile = make_profile(make_user(), first_name='Asha')
        acharya = Acharya.objects.create(kendra=self.kendra, acharya_id=profile)
        homepage = HomePage.objects.create(tagline='t', description='d')

        self.assertEqual(str(self.kendra), 'Kendra One')
        self.assertEqual(str(category), 'Kendra One - Yoga')
        self.assertEqual(str(activity), 'Kendra One - Morning yoga (Yoga)')
        self.assertEqual(str(student), 'Ravi')
        self.assertEqual(str(event), 'Kendra One - Annual day')
        self.assertEqual(str(acharya), 'Asha')
        self.assertEqual(str(homepage), 'Anandakendra Home Page Content')

    @unittest.expectedFailure
    def test_photo_str_returns_string(self):
        """Bug: Photo.__str__ returns the FieldFile object instead of a str
        (applications/anandakendra/models.py:108), so str(photo) raises TypeError."""
        photo = Photo.objects.create(kendra=self.kendra, picture=image_upload())
        self.assertIsInstance(str(photo), str)

    def test_cover_photo_prefers_approved_then_falls_back(self):
        category = ActivityCategory.objects.create(kendra=self.kendra, name='Yoga')
        activity = Activity.objects.create(
            category=category, name='Act', description='d', activity_time='6am',
        )
        self.assertIsNone(activity.cover_photo)
        pending = Photo.objects.create(
            kendra=self.kendra, activity=activity, picture=image_upload('a.gif'),
        )
        self.assertEqual(activity.cover_photo, pending)
        approved = Photo.objects.create(
            kendra=self.kendra, activity=activity, picture=image_upload('b.gif'), approved=True,
        )
        self.assertEqual(activity.cover_photo, approved)


class IndexAndDetailTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.kendra = make_kendra()
        self.detail_url = reverse('anandakendra:AnandkendraDetail', args=[self.kendra.slug])

    def test_index_lists_kendras_and_homepage_content(self):
        homepage = HomePage.objects.create(
            tagline='Tag', description='Desc', picture=image_upload('index.gif'),
        )
        response = self.client.get(reverse('anandakendra:anandakendra'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['kendras']), [self.kendra])
        self.assertEqual(response.context['content'], homepage)
        self.assertContains(response, self.kendra.name)

    def test_detail_404_for_unknown_slug(self):
        self.assertEqual(
            self.client.get(reverse('anandakendra:AnandkendraDetail', args=['nope'])).status_code,
            404,
        )

    def test_detail_anonymous_shows_only_approved_photos(self):
        approved = Photo.objects.create(
            kendra=self.kendra, picture=image_upload('ok.gif'), approved=True,
        )
        Photo.objects.create(kendra=self.kendra, picture=image_upload('pending.gif'))
        category = ActivityCategory.objects.create(kendra=self.kendra, name='Yoga')
        Activity.objects.create(
            category=category, name='Morning yoga', description='d', activity_time='6am',
        )
        Event.objects.create(
            kendra=self.kendra, name='Annual day', description='d', date='2024-01-01',
            thumb=image_upload('thumb.gif'),
        )
        Student.objects.create(
            kendra=self.kendra, name='Ravi', guardian_name='G', school_class='5',
            contact_no='1', address='a',
        )

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        ctx = response.context
        self.assertEqual(list(ctx['photos']), [approved])
        self.assertFalse(ctx['check_admin'])
        self.assertTrue(ctx['has_activities'])
        self.assertEqual(ctx['events'].count(), 1)
        self.assertEqual(ctx['students'].count(), 1)
        self.assertFalse(ctx['open_signup_modal'])
        self.assertEqual(ctx['kendra_hero_locality_css'], 'Cuttack')

    def test_detail_admin_sees_admin_flag_and_unassigned_acharya_choices(self):
        admin = make_admin()
        assigned = make_profile(make_user('a@example.com'), first_name='Assigned')
        free = make_profile(make_user('b@example.com'), first_name='Free')
        Acharya.objects.create(kendra=self.kendra, acharya_id=assigned)

        self.client.force_login(admin)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['check_admin'])
        self.assertEqual(list(response.context['acharya_choices']), [free])
        self.assertFalse(response.context['has_activities'])

    def test_detail_signup_modal_prefill_from_session(self):
        session = self.client.session
        session['signup_modal_prefill_email'] = 'new@example.com'
        session.save()
        response = self.client.get(self.detail_url + '?signup_modal=1')
        self.assertTrue(response.context['open_signup_modal'])
        self.assertEqual(response.context['signup_form'].initial, {'email': 'new@example.com'})
        self.assertNotIn('signup_modal_prefill_email', self.client.session)


class LoginRequiredTests(TestCase):
    def test_all_mutating_views_redirect_anonymous(self):
        for name in (
            'CreateAnandaKendra', 'AddAcharya', 'EnrollStudent',
            'AnandakendraAddActivityCategory', 'AnandakendraCreateActivity',
            'AnandakendraAddToGallery', 'AdminImageApproval', 'CreateEventAnandakendra',
        ):
            url = reverse(f'anandakendra:{name}')
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 302, name)
            self.assertTrue(response['Location'].startswith(LOGIN_URL), name)

    def test_get_on_mutating_views_redirects_home(self):
        self.client.force_login(make_user())
        for name in (
            'AddAcharya', 'EnrollStudent', 'AnandakendraAddActivityCategory',
            'AnandakendraCreateActivity', 'AnandakendraAddToGallery',
            'AdminImageApproval', 'CreateEventAnandakendra',
        ):
            response = self.client.get(reverse(f'anandakendra:{name}'))
            self.assertRedirects(response, '/', fetch_redirect_response=False, msg_prefix=name)
        response = self.client.get(reverse('anandakendra:CreateAnandaKendra'))
        self.assertRedirects(response, reverse('anandakendra:anandakendra'),
                             fetch_redirect_response=False)


class CreateKendraTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client.force_login(make_admin())
        self.url = reverse('anandakendra:CreateAnandaKendra')

    def test_creates_kendra_with_slug_and_redirects_to_detail(self):
        response = self.client.post(self.url, {
            'name': 'New Kendra', 'locality': 'Puri Town', 'description': 'd',
            'address': 'addr', 'image': image_upload(),
        })
        kendra = AnandaKendra.objects.get(name='New Kendra')
        self.assertEqual(kendra.slug, 'new-kendra-puri-town')
        self.assertTrue(kendra.image.name)
        self.assertRedirects(
            response, reverse('anandakendra:AnandkendraDetail', args=[kendra.slug]),
            fetch_redirect_response=False,
        )

    def test_duplicate_name_and_locality_rejected(self):
        make_kendra()
        response = self.client.post(self.url, {
            'name': 'Kendra One', 'locality': 'Cuttack', 'description': 'd', 'address': 'a',
        }, follow=True)
        self.assertEqual(AnandaKendra.objects.count(), 1)
        self.assertRedirects(response, reverse('anandakendra:anandakendra'))
        self.assertIn('already exists', [m.message for m in response.context['messages']][0])


class DetailMutationTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.kendra = make_kendra()
        self.slug = self.kendra.slug
        self.detail_url = f'/anandakendra/detail/{self.slug}/'
        self.admin = make_admin()
        self.client.force_login(self.admin)

    def test_enroll_student(self):
        response = self.client.post(reverse('anandakendra:EnrollStudent'), {
            'slug': self.slug, 'name': 'Ravi', 'gender': 'F', 'guardian_name': 'Guardian',
            'school_class': '7', 'contact_no': '9999', 'address': 'Village',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        student = Student.objects.get()
        self.assertEqual((student.kendra, student.gender, student.school_class),
                         (self.kendra, 'F', '7'))

    def test_enroll_student_unknown_kendra_404(self):
        response = self.client.post(reverse('anandakendra:EnrollStudent'), {'slug': 'x'})
        self.assertEqual(response.status_code, 404)

    def test_add_acharya_requires_selection(self):
        response = self.client.post(reverse('anandakendra:AddAcharya'), {
            'slug': self.slug, 'acharya_1': '', 'acharya_2': ' ',
        }, follow=True)
        self.assertEqual(Acharya.objects.count(), 0)
        self.assertIn('Select at least one', [m.message for m in response.context['messages']][0])

    def test_add_acharya_creates_rows_and_dedupes(self):
        p1 = make_profile(make_user('one@example.com'), first_name='One')
        p2 = make_profile(make_user('two@example.com'), first_name='Two')
        response = self.client.post(reverse('anandakendra:AddAcharya'), {
            'slug': self.slug, 'acharya_1': 'one@example.com', 'acharya_2': 'one@example.com',
        }, follow=True)
        self.assertEqual(Acharya.objects.filter(kendra=self.kendra).count(), 1)
        self.assertIn('Added 1 acharya', [m.message for m in response.context['messages']][0])

        # Second submit: p1 already assigned, unknown email ignored, p2 added.
        response = self.client.post(reverse('anandakendra:AddAcharya'), {
            'slug': self.slug, 'acharya_1': 'one@example.com', 'acharya_2': 'two@example.com',
        }, follow=True)
        self.assertEqual(
            set(Acharya.objects.filter(kendra=self.kendra).values_list('acharya_id', flat=True)),
            {p1.pk, p2.pk},
        )

        response = self.client.post(reverse('anandakendra:AddAcharya'), {
            'slug': self.slug, 'acharya_1': 'nobody@example.com',
        }, follow=True)
        self.assertEqual(Acharya.objects.count(), 2)
        self.assertIn('No new acharyas', [m.message for m in response.context['messages']][0])

    def test_add_activity_category(self):
        response = self.client.post(reverse('anandakendra:AnandakendraAddActivityCategory'), {
            'slug': self.slug, 'name': 'Sports',
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertTrue(ActivityCategory.objects.filter(kendra=self.kendra, name='Sports').exists())

    def test_create_activity_with_images(self):
        category = ActivityCategory.objects.create(kendra=self.kendra, name='Sports')
        response = self.client.post(reverse('anandakendra:AnandakendraCreateActivity'), {
            'slug': self.slug, 'activity_name': 'Football', 'category': str(category.pk),
            'description': 'kick', 'activity_time': 'Sunday',
            'activity_images': [image_upload('a.gif'), image_upload('b.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        activity = Activity.objects.get(name='Football')
        self.assertEqual(activity.category, category)
        photos = Photo.objects.filter(activity=activity, kendra=self.kendra)
        self.assertEqual(photos.count(), 2)
        self.assertTrue(all(p.approved for p in photos))

    def test_create_activity_unknown_category_404(self):
        response = self.client.post(reverse('anandakendra:AnandakendraCreateActivity'), {
            'slug': self.slug, 'activity_name': 'x', 'category': '999',
            'description': 'd', 'activity_time': 't',
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Activity.objects.count(), 0)

    def test_gallery_upload_admin_auto_approved(self):
        response = self.client.post(reverse('anandakendra:AnandakendraAddToGallery'), {
            'slug': self.slug, 'gallery_images': [image_upload('g.gif')],
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        self.assertTrue(Photo.objects.get(kendra=self.kendra).approved)

    def test_gallery_upload_member_pending(self):
        self.client.force_login(make_user())
        self.client.post(reverse('anandakendra:AnandakendraAddToGallery'), {
            'slug': self.slug, 'gallery_images': [image_upload('g.gif')],
        })
        self.assertFalse(Photo.objects.get(kendra=self.kendra).approved)

    def test_create_event(self):
        response = self.client.post(reverse('anandakendra:CreateEventAnandakendra'), {
            'slug': self.slug, 'event_name': 'Fest', 'event_date': '2024-03-01',
            'description': 'fun', 'event_thumb': image_upload('e.gif'),
        })
        self.assertRedirects(response, self.detail_url, fetch_redirect_response=False)
        event = Event.objects.get(name='Fest')
        self.assertEqual(str(event.date), '2024-03-01')
        self.assertTrue(event.thumb.name)


class AdminApprovalTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.kendra = make_kendra()
        self.photo = Photo.objects.create(kendra=self.kendra, picture=image_upload('p.gif'))
        self.client.force_login(make_admin())
        self.url = reverse('anandakendra:AdminImageApproval')

    def test_approve_redirects_to_detail(self):
        response = self.client.post(self.url, {
            'kendra': self.kendra.slug, 'image': self.photo.pk, 'status': 'approve',
        })
        self.assertRedirects(response, f'/anandakendra/detail/{self.kendra.slug}/',
                             fetch_redirect_response=False)
        self.photo.refresh_from_db()
        self.assertTrue(self.photo.approved)

    def test_reject_deletes_photo_and_file_and_returns_json_for_ajax(self):
        path = self.photo.picture.path
        self.assertTrue(os.path.isfile(path))
        response = self.client.post(self.url, {
            'kendra': self.kendra.slug, 'image': self.photo.pk, 'status': 'reject',
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.json()), [])
        self.assertFalse(Photo.objects.filter(pk=self.photo.pk).exists())
        self.assertFalse(os.path.exists(path))

    def test_unknown_photo_404(self):
        response = self.client.post(self.url, {
            'kendra': self.kendra.slug, 'image': 9999, 'status': 'approve',
        })
        self.assertEqual(response.status_code, 404)


class AdminSiteTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.kendra = make_kendra()
        self.client.force_login(make_admin())

    def test_get_kendra_helpers(self):
        category = ActivityCategory.objects.create(kendra=self.kendra, name='Yoga')
        activity = Activity.objects.create(
            category=category, name='Act', description='d', activity_time='t',
        )
        event = Event.objects.create(
            kendra=self.kendra, name='Ev', description='d', date='2024-01-01',
            thumb=image_upload('t.gif'),
        )
        self.assertEqual(
            admin_site._registry[ActivityCategory].get_kendra(category), 'Kendra One')
        self.assertEqual(admin_site._registry[Activity].get_kendra(activity), 'Kendra One')
        self.assertEqual(admin_site._registry[Event].get_kendra(event), 'Kendra One')
        self.assertIsInstance(admin_site._registry[Photo], kendra_admin.PhotoAdmin)

    def test_changelists_render(self):
        for model in (AnandaKendra, ActivityCategory, Activity, Event, Student, Acharya, Photo):
            url = reverse(f'admin:anandakendra_{model._meta.model_name}_changelist')
            self.assertEqual(self.client.get(url).status_code, 200, model)

    def test_response_add_redirects_to_detail_when_next_given(self):
        url = reverse('admin:anandakendra_anandakendra_add') + '?next=anandakendra_details'
        data = {
            'name': 'Admin Kendra', 'locality': 'Bhubaneswar', 'slug': 'admin-kendra-bhubaneswar',
            'address': 'a', 'description': 'd', 'image': image_upload('h.gif'),
            'image_caption_en': '', 'image_caption_or': '',
        }
        response = self.client.post(url, data)
        self.assertRedirects(
            response, reverse('anandakendra:AnandkendraDetail', args=['admin-kendra-bhubaneswar']),
            fetch_redirect_response=False,
        )
        self.assertTrue(AnandaKendra.objects.filter(slug='admin-kendra-bhubaneswar').exists())

    def test_response_add_default_behaviour_without_next(self):
        url = reverse('admin:anandakendra_anandakendra_add')
        data = {
            'name': 'Plain Kendra', 'locality': 'Puri', 'slug': 'plain-kendra-puri',
            'address': 'a', 'description': 'd', 'image': image_upload('h.gif'),
            'image_caption_en': '', 'image_caption_or': '',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('admin:anandakendra_anandakendra_changelist'),
                             fetch_redirect_response=False)
