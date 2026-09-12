"""Landing page (React shell) and /api/landing/ payload contract."""

import json
from unittest import mock

from django.test import TestCase

from applications.patriotism import models as patriotism_models
from bandhuapp.models import HeroSlide, HomePage
from bandhuapp.tests.support import TempMediaMixin, make_admin, make_profile, make_user

# Keys `frontend/src/App.jsx` reads from the injected JSON. Removing one breaks the landing page.
LANDING_KEYS = {
    'initiatives', 'about', 'mission', 'recent_events', 'volunteer', 'photos', 'content',
    'banner_image', 'current_updates', 'people_designations', 'videos', 'contact',
    'annual_reports', 'recent_activities', 'urls', 'user', 'logo_url', 'about_slides',
    'profile_photos', 'visitors', 'hero_slides', 'hero_photos', 'initiative_nav', 'webteam',
}
LANDING_URL_KEYS = {
    'login', 'signup', 'ankurayan', 'anandakendra', 'ashram', 'charity_work',
    'initiative_patriotism', 'initiative_raktadan', 'initiative_sevavrata', 'publications',
    'people', 'home', 'sanskar', 'swaraj', 'swabalamban', 'annual_reports_upload',
}
NAV_KEYS = {'show_initiative_patriotism', 'show_initiative_raktadan', 'show_initiative_sevavrata'}
MISSION_KEYS = {
    'sanskar_tagline', 'sanskar_desc', 'sanskar_images',
    'swaraj_tagline', 'swaraj_desc', 'swaraj_images',
    'swabalamban_tagline', 'swabalamban_desc', 'swabalamban_images',
}


class LandingApiTests(TempMediaMixin, TestCase):
    def setUp(self):
        # Video durations are scraped from YouTube; never touch the network in tests.
        patcher = mock.patch('bandhuapp.views.enrich_video_durations')
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_payload(self):
        response = self.client.get('/api/landing/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        return json.loads(response.content)

    def test_payload_contains_every_key_the_frontend_reads(self):
        data = self.get_payload()
        self.assertTrue(LANDING_KEYS <= set(data), LANDING_KEYS - set(data))
        self.assertEqual(set(data['urls']), LANDING_URL_KEYS)
        self.assertEqual(set(data['initiative_nav']), NAV_KEYS)
        self.assertEqual(set(data['mission']), MISSION_KEYS)
        for list_key in ('recent_events', 'photos', 'current_updates', 'videos', 'annual_reports',
                         'recent_activities', 'about_slides', 'profile_photos', 'visitors',
                         'hero_slides', 'hero_photos', 'people_designations'):
            self.assertIsInstance(data[list_key], list, list_key)

    def test_anonymous_user_block(self):
        data = self.get_payload()
        self.assertEqual(data['user'], {'is_authenticated': False, 'is_admin': False})
        self.assertEqual(data['initiative_nav'], {key: False for key in NAV_KEYS})

    def test_admin_user_block_and_nav(self):
        self.client.force_login(make_admin())
        data = self.get_payload()
        self.assertEqual(data['user'], {'is_authenticated': True, 'is_admin': True})
        self.assertEqual(data['initiative_nav'], {key: True for key in NAV_KEYS})

    def test_published_program_entry_turns_on_public_nav_flag(self):
        patriotism_models.Ashram.objects.create(
            name='Quiz 2024', locality='Cuttack', description='d', address='a',
            image='tests/hero.gif', slug='quiz-2024', reports='Report',
        )
        data = self.get_payload()
        self.assertTrue(data['initiative_nav']['show_initiative_patriotism'])
        self.assertFalse(data['initiative_nav']['show_initiative_raktadan'])

    def test_member_without_profile_gets_400(self):
        self.client.force_login(make_user())
        response = self.client.get('/api/landing/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content), {'error': 'Complete your profile first'})

    def test_member_with_profile_gets_payload(self):
        member = make_user()
        make_profile(member)
        self.client.force_login(member)
        data = self.get_payload()
        self.assertEqual(data['user'], {'is_authenticated': True, 'is_admin': False})

    def test_only_get_is_allowed(self):
        self.assertEqual(self.client.post('/api/landing/').status_code, 405)

    def test_hero_slide_html_is_not_escaped(self):
        # Hero.jsx renders these via dangerouslySetInnerHTML; the payload must carry
        # the admin's raw markup, not an HTML-escaped copy, or the tags show up as text.
        HeroSlide.objects.create(
            title='<span class="text-[#004f57]">ବନ୍ଧୁଘର</span>',
            subtitle='<p>one</p><p><strong>two</strong></p>',
        )
        data = self.get_payload()
        self.assertEqual(data['hero_slides'][0]['title'], '<span class="text-[#004f57]">ବନ୍ଧୁଘର</span>')
        self.assertEqual(data['hero_slides'][0]['subtitle'], '<p>one</p><p><strong>two</strong></p>')


class LandingPageTests(TempMediaMixin, TestCase):
    def setUp(self):
        patcher = mock.patch('bandhuapp.views.enrich_video_durations')
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_react_shell_embeds_landing_data(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="landing-data"')
        self.assertTrue(LANDING_KEYS <= set(response.context['landing_data']))
        self.assertIn('auth_modal', response.context['landing_data'])
        self.assertIn('csrf_token', response.context['landing_data'])

    def test_member_without_profile_is_sent_to_profile_page(self):
        self.client.force_login(make_user())
        self.assertRedirects(self.client.get('/'), '/profile/', fetch_redirect_response=False)

    def test_visitor_count_increments_once_per_session(self):
        home = HomePage.objects.create(banner_image='tests/banner.gif', visitors_count=0)
        self.client.get('/')
        self.client.get('/')
        home.refresh_from_db()
        self.assertEqual(home.visitors_count, 1)

    def test_login_modal_query_opens_modal(self):
        response = self.client.get('/?login_modal=1&next=/people/')
        modal = response.context['landing_data']['auth_modal']
        self.assertTrue(modal['open_from_url'])
        self.assertEqual(modal['next'], '/people/')

    def test_unsafe_next_falls_back_to_home(self):
        response = self.client.get('/?login_modal=1&next=https://evil.example')
        self.assertEqual(response.context['landing_data']['auth_modal']['next'], '/')
