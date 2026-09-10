"""`is_admin` template filter — the single gate for on-page admin controls."""

from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import TestCase

from bandhuapp.templatetags.permissions import is_admin
from bandhuapp.tests.support import make_admin, make_user


class IsAdminFilterTests(TestCase):
    def test_anonymous_is_not_admin(self):
        self.assertFalse(is_admin(AnonymousUser()))

    def test_plain_member_is_not_admin(self):
        self.assertFalse(is_admin(make_user('plain@example.com')))

    def test_staff_flag_alone_is_not_admin(self):
        self.assertFalse(is_admin(make_user('staff@example.com', is_staff=True)))

    def test_is_admin_flag_grants_admin(self):
        self.assertTrue(is_admin(make_admin()))

    def test_filter_is_usable_from_templates(self):
        template = Template('{% load permissions %}{% if user|is_admin %}ADMIN{% else %}PUBLIC{% endif %}')
        self.assertEqual(template.render(Context({'user': make_admin()})), 'ADMIN')
        self.assertEqual(template.render(Context({'user': AnonymousUser()})), 'PUBLIC')
