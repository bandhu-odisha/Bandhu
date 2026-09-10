"""Every mounted public page must render for anonymous visitors and for admins."""

import unittest

from django.test import TestCase

from bandhuapp.tests.support import TempMediaMixin, make_admin

PUBLIC_PAGES = [
    '/',
    '/classic/',
    '/api/landing/',
    '/people/',
    '/sanskar/',
    '/swaraj/',
    '/swabalamban/',
    '/anandakendra/',
    '/ankurayan/',
    '/bandhughar/',
    '/other_activities/',
    '/prasanta-raktadan-shibir/',
    '/patriotism-in-action/',
    '/odisha-satabdi-sevavrata/',
    '/publications/',
    '/accounts/login/',
    '/accounts/signup/',
    '/accounts/signup/success/',
    '/accounts/activated/',
    '/accounts/authenticated/',
    '/accounts/deleted/',
    '/accounts/password_reset/',
    '/accounts/password_reset/done/',
    '/accounts/reset/done/',
]

LOGIN_REQUIRED_PAGES = [
    '/profile/',
    '/accounts/password_change/',
    '/annual-reports/upload/',
]


class PublicUrlSmokeTests(TempMediaMixin, TestCase):
    def test_public_pages_render_for_anonymous(self):
        for path in PUBLIC_PAGES:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_public_pages_render_for_admin(self):
        """Admin sessions render the on-page admin controls on every public page."""
        self.client.force_login(make_admin())
        for path in PUBLIC_PAGES:
            if path.startswith('/accounts/login') or path.startswith('/accounts/signup/'):
                continue  # login/signup redirect authenticated users
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_login_required_pages_redirect_anonymous(self):
        for path in LOGIN_REQUIRED_PAGES:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response['Location'].startswith('/accounts/login/'))

    def test_django_admin_redirects_anonymous(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_unknown_path_is_404(self):
        self.assertEqual(self.client.get('/no-such-page/').status_code, 404)

    @unittest.expectedFailure
    def test_url_only_shell_apps_render(self):
        """madhmukti / sanskarbarga views render templates that are not in git.

        `.gitignore` drops `*.html`; `madhmukti/index.html` and
        `sanskarbarga/index.html` were never force-added, so both URLs raise
        TemplateDoesNotExist. Flip this to a normal test once the templates land.
        """
        for path in ('/sanskarbarga/', '/madh_mukti/'):
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_login_and_signup_redirect_authenticated_users_home(self):
        self.client.force_login(make_admin())
        for path in ('/accounts/login/', '/accounts/signup/'):
            with self.subTest(path=path):
                self.assertRedirects(self.client.get(path), '/', fetch_redirect_response=False)
