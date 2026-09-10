"""Bandhughar views not covered by test_views.py: meetings, attendees, categories, activities, gallery."""

import unittest
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from applications.ashram.models import (
    Activity, ActivityCategory, Ashram, Attendee, Event, HomePage, Meeting, Photo,
)
from bandhuapp.tests.support import (
    TempMediaMixin, file_upload, image_upload, make_admin, make_profile, make_user,
)

LOGIN = '/accounts/login/'


def make_ashram(name='Bandhughar One', locality='Cuttack', slug='bandhughar-one-cuttack'):
    return Ashram.objects.create(
        name=name, locality=locality, description='d', address='a', image='tests/hero.gif', slug=slug,
    )


def make_meeting(ashram, topic='Planning', schedule=None):
    schedule = schedule or timezone.make_aware(datetime(2024, 3, 1, 0, 0))
    return Meeting.objects.create(
        ashram=ashram, topic=topic, agenda='agenda', location='hall',
        schedule=schedule, minutes='tests/minutes.pdf',
    )


class LoginRequiredTests(TestCase):
    """Every mutating view redirects anonymous users to the login page."""

    def test_anonymous_posts_redirect_to_login(self):
        for url in (
            '/bandhughar/add/meeting/', '/bandhughar/add/attendee/',
            '/bandhughar/add/activity/category/', '/bandhughar/create/activity/',
            '/bandhughar/add/gallery/',
        ):
            response = self.client.post(url, {})
            self.assertEqual(response.status_code, 302, url)
            self.assertTrue(response['Location'].startswith(LOGIN), url)


class GetFallbackTests(TestCase):
    """Logged-in GETs on POST-only views bounce to the site root without side effects."""

    def test_get_redirects_home(self):
        self.client.force_login(make_user())
        for url in (
            '/bandhughar/add/meeting/', '/bandhughar/add/attendee/',
            '/bandhughar/add/activity/category/', '/bandhughar/create/activity/',
            '/bandhughar/add/gallery/', '/bandhughar/admin_approval/',
            '/bandhughar/create/event/',
        ):
            self.assertRedirects(self.client.get(url), '/', fetch_redirect_response=False, msg_prefix=url)
        self.assertRedirects(self.client.get('/bandhughar/new/'), '/bandhughar/', fetch_redirect_response=False)


class MeetingAndAttendeeTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.ashram = make_ashram()
        self.client.force_login(make_admin())

    def test_add_meeting_creates_row_and_redirects_to_detail(self):
        response = self.client.post('/bandhughar/add/meeting/', {
            'slug': self.ashram.slug, 'topic': 'Budget', 'agenda': 'Spend less',
            'schedule': '2024-03-01', 'location': 'Hall', 'minutes': file_upload('minutes.pdf'),
        })
        self.assertRedirects(response, f'/bandhughar/detail/{self.ashram.slug}/', fetch_redirect_response=False)
        meeting = Meeting.objects.get(ashram=self.ashram)
        self.assertEqual((meeting.topic, meeting.location, meeting.agenda), ('Budget', 'Hall', 'Spend less'))
        self.assertTrue(meeting.minutes.name.startswith('ashram/meeting/'))
        self.assertIn('minutes', meeting.minutes.name)

    def test_add_meeting_unknown_ashram_is_404(self):
        response = self.client.post('/bandhughar/add/meeting/', {
            'slug': 'missing', 'topic': 't', 'agenda': 'a', 'schedule': '2024-03-01', 'location': 'l',
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Meeting.objects.count(), 0)

    def test_detail_lists_meetings_for_admin(self):
        meeting = make_meeting(self.ashram, topic='Quarterly')
        response = self.client.get(f'/bandhughar/detail/{self.ashram.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['meetings']), [meeting])
        self.assertTrue(response.context['check_admin'])
        self.assertTrue(response.context['show_gallery'])
        # NOTE: the Meetings section markup in ashram_detail.html is wrapped in a
        # {% comment %}...{% endcomment %} block (lines 444-688), so the meeting
        # topic is currently never rendered even though it's in the context above.
        # Not asserted here (assertContains/assertNotContains) so this test doesn't
        # start failing the moment that block is re-enabled.

    def test_add_guest_attendee_by_name(self):
        meeting = make_meeting(self.ashram, topic='Planning')
        response = self.client.post('/bandhughar/add/attendee/', {
            'schedule': '2024-03-01', 'topic': 'Planning', 'slug': self.ashram.slug,
            'name': 'Guest Person', 'email': 'guest@example.com', 'contact_no': '9999999999',
            'attendes': '',
        })
        self.assertRedirects(response, f'/bandhughar/detail/{self.ashram.slug}/', fetch_redirect_response=False)
        attendee = Attendee.objects.get(meeting=meeting)
        self.assertEqual(attendee.name, 'Guest Person')
        self.assertEqual(attendee.email, 'guest@example.com')
        self.assertIsNone(attendee.profile)
        # Attendee.__str__ is "{ashram.name} - {meeting.schedule} - {name}" — it doesn't
        # include the meeting topic. Use the DB-fetched meeting (not the in-memory one) so
        # the schedule's timezone representation matches what __str__ actually renders.
        self.assertEqual(
            str(attendee),
            f'{self.ashram.name} - {attendee.meeting.schedule} - Guest Person',
        )

    def test_add_member_attendees_from_profile_emails(self):
        meeting = make_meeting(self.ashram, topic='Planning')
        one = make_profile(make_user('one@example.com'), first_name='One', last_name='Member', contact_no='1111111111')
        two = make_profile(make_user('two@example.com'), first_name='Two', last_name='Member', contact_no='2222222222')
        response = self.client.post('/bandhughar/add/attendee/', {
            'schedule': '2024-03-01', 'topic': 'Planning', 'slug': self.ashram.slug,
            'name': '', 'email': '', 'contact_no': '',
            'attendes': 'one@example.com,two@example.com',
        })
        self.assertEqual(response.status_code, 302)
        attendees = Attendee.objects.filter(meeting=meeting).order_by('id')
        self.assertEqual([a.profile for a in attendees], [one, two])
        # Attendee.save() copies contact details from the linked profile.
        self.assertEqual(attendees[0].name, 'One Member')
        self.assertEqual(attendees[0].email, 'one@example.com')
        self.assertEqual(attendees[1].contact_no, '2222222222')

    @unittest.expectedFailure
    def test_add_attendee_for_unknown_meeting_should_not_crash(self):
        """Bug: applications/ashram/views.py:99-108 — when no Meeting matches the posted
        schedule/topic, `meeting` is None and Attendee.objects.create(meeting=None) raises
        IntegrityError (NOT NULL on meeting_id), producing a 500 instead of a redirect."""
        response = self.client.post('/bandhughar/add/attendee/', {
            'schedule': '2024-03-01', 'topic': 'Nope', 'slug': self.ashram.slug,
            'name': 'Guest', 'email': 'g@example.com', 'contact_no': '1', 'attendes': '',
        })
        self.assertEqual(response.status_code, 302)


class ActivityTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.ashram = make_ashram()
        self.client.force_login(make_admin())

    def test_add_activity_category(self):
        response = self.client.post('/bandhughar/add/activity/category/', {
            'slug': self.ashram.slug, 'name': 'Health',
        })
        self.assertRedirects(response, f'/bandhughar/detail/{self.ashram.slug}/', fetch_redirect_response=False)
        category = ActivityCategory.objects.get(ashram=self.ashram)
        self.assertEqual(category.name, 'Health')
        self.assertEqual(str(category), 'Bandhughar One - Health')

    def test_add_activity_category_unknown_ashram_is_404(self):
        self.assertEqual(
            self.client.post('/bandhughar/add/activity/category/', {'slug': 'nope', 'name': 'x'}).status_code, 404,
        )
        self.assertEqual(ActivityCategory.objects.count(), 0)

    def test_create_activity_with_images_creates_approved_photos(self):
        category = ActivityCategory.objects.create(ashram=self.ashram, name='Health')
        response = self.client.post('/bandhughar/create/activity/', {
            'slug': self.ashram.slug, 'activity_name': 'Camp', 'category': category.pk,
            'description': 'Free checkups',
            'activity_images': [image_upload('a.gif'), image_upload('b.gif')],
        })
        self.assertRedirects(response, f'/bandhughar/detail/{self.ashram.slug}/', fetch_redirect_response=False)
        activity = Activity.objects.get(category=category)
        self.assertEqual(activity.name, 'Camp')
        self.assertEqual(str(activity), 'Bandhughar One - Camp (Health)')
        photos = Photo.objects.filter(ashram=self.ashram, activity=activity)
        self.assertEqual(photos.count(), 2)
        self.assertTrue(all(p.approved for p in photos))

        detail = self.client.get(f'/bandhughar/detail/{self.ashram.slug}/')
        self.assertTrue(detail.context['has_activities'])
        self.assertEqual(detail.context['photos'].count(), 2)
        self.assertContains(detail, 'Camp')

    def test_create_activity_without_images(self):
        category = ActivityCategory.objects.create(ashram=self.ashram, name='Health')
        self.client.post('/bandhughar/create/activity/', {
            'slug': self.ashram.slug, 'activity_name': 'Talk', 'category': category.pk, 'description': 'd',
        })
        self.assertEqual(Activity.objects.count(), 1)
        self.assertEqual(Photo.objects.count(), 0)

    def test_create_activity_unknown_category_is_404(self):
        response = self.client.post('/bandhughar/create/activity/', {
            'slug': self.ashram.slug, 'activity_name': 'x', 'category': 999, 'description': 'd',
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Activity.objects.count(), 0)


class GalleryTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.ashram = make_ashram()
        self.client.force_login(make_user())

    def test_add_to_gallery_without_files_only_redirects(self):
        response = self.client.post('/bandhughar/add/gallery/', {'slug': self.ashram.slug})
        self.assertRedirects(response, f'/bandhughar/detail/{self.ashram.slug}/', fetch_redirect_response=False)
        self.assertEqual(Photo.objects.count(), 0)

    def test_add_to_gallery_unknown_ashram_is_404(self):
        self.assertEqual(self.client.post('/bandhughar/add/gallery/', {'slug': 'nope'}).status_code, 404)

    @unittest.expectedFailure
    def test_add_to_gallery_uploads_unapproved_photos(self):
        """Bug: applications/ashram/views.py:181 reads `ashram.admin`, but the `admin` field on
        Ashram is commented out (models.py:20), so any gallery upload with at least one file
        raises AttributeError (500). Expected behaviour: photos saved with approved=False."""
        response = self.client.post('/bandhughar/add/gallery/', {
            'slug': self.ashram.slug, 'gallery_images': [image_upload('g1.gif'), image_upload('g2.gif')],
        })
        self.assertEqual(response.status_code, 302)
        photos = Photo.objects.filter(ashram=self.ashram)
        self.assertEqual(photos.count(), 2)
        self.assertFalse(any(p.approved for p in photos))


class DetailContextTests(TempMediaMixin, TestCase):
    def test_public_visitor_sees_only_approved_photos_and_no_gallery_when_empty(self):
        ashram = make_ashram()
        Photo.objects.create(ashram=ashram, picture='tests/p.gif', approved=False)
        response = self.client.get(f'/bandhughar/detail/{ashram.slug}/')
        self.assertFalse(response.context['check_admin'])
        self.assertFalse(response.context['show_gallery'])
        self.assertEqual(response.context['photos'].count(), 0)
        self.assertEqual(response.context['unapproved_photos'].count(), 1)
        self.assertFalse(response.context['has_events'])
        self.assertFalse(response.context['has_activities'])

    def test_events_and_homepage_content_flow_into_context(self):
        ashram = make_ashram()
        event = Event.objects.create(ashram=ashram, name='Fair', description='d', thumb='tests/e.gif', date='2024-01-01')
        home = HomePage.objects.create(tagline='Tag', description='Desc')
        response = self.client.get(f'/bandhughar/detail/{ashram.slug}/')
        self.assertTrue(response.context['has_events'])
        self.assertEqual(list(response.context['events']), [event])
        self.assertEqual(response.context['content'], home)
        self.assertEqual(str(event), 'Bandhughar One - Fair')
        self.assertEqual(str(home), 'Bandhughar Home Page Content')

        index = self.client.get('/bandhughar/')
        self.assertEqual(index.context['content'], home)
        self.assertContains(index, 'Tag')


class ModelStrTests(TestCase):
    def test_str_representations(self):
        ashram = make_ashram()
        meeting = make_meeting(ashram, topic='Sync')
        self.assertEqual(str(ashram), 'Bandhughar One - Cuttack')
        self.assertTrue(str(meeting).startswith('Bandhughar One - Sync ('))


class AshramAdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client.force_login(make_admin())

    def test_changelist_and_add_form_render(self):
        make_ashram()
        self.assertEqual(self.client.get('/admin/ashram/ashram/').status_code, 200)
        self.assertEqual(self.client.get('/admin/ashram/ashram/add/').status_code, 200)
        for model in ('activitycategory', 'activity', 'event', 'meeting', 'attendee', 'photo', 'homepage'):
            self.assertEqual(self.client.get(f'/admin/ashram/{model}/').status_code, 200, model)

    def _add_payload(self, **overrides):
        data = {
            'name': 'New Ghar', 'locality': 'Puri', 'slug': 'new-ghar-puri', 'address': 'a',
            'description': 'd', 'image': image_upload(), 'image_caption_en': '', 'image_caption_or': '',
        }
        data.update(overrides)
        return data

    def test_response_add_redirects_to_public_detail_when_next_is_bandhughar_details(self):
        response = self.client.post('/admin/ashram/ashram/add/?next=bandhughar_details', self._add_payload())
        self.assertRedirects(response, '/bandhughar/detail/new-ghar-puri/', fetch_redirect_response=False)
        self.assertTrue(Ashram.objects.filter(slug='new-ghar-puri').exists())

    def test_response_add_default_goes_back_to_changelist(self):
        response = self.client.post('/admin/ashram/ashram/add/', self._add_payload())
        self.assertRedirects(response, '/admin/ashram/ashram/', fetch_redirect_response=False)
