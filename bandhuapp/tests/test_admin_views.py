"""Django admin: every registered model's changelist and add form must render."""

import unittest

from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from bandhuapp.tests.support import TempMediaMixin, make_admin, make_user


class DjangoAdminSmokeTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client.force_login(make_admin())

    def test_index_renders(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bandhu')

    def test_every_registered_model_changelist_and_add_render(self):
        self.assertGreater(len(admin.site._registry), 20)
        for model, model_admin in admin.site._registry.items():
            info = (model._meta.app_label, model._meta.model_name)
            with self.subTest(model='%s.%s' % info):
                response = self.client.get(reverse('admin:%s_%s_changelist' % info))
                self.assertEqual(response.status_code, 200)
                if info == ('accounts', 'user'):
                    continue  # add view is broken; see test_add_user_form_renders
                response = self.client.get(reverse('admin:%s_%s_add' % info))
                expected = 200 if model_admin.has_add_permission(response.wsgi_request) else 403
                self.assertEqual(response.status_code, expected)

    @unittest.expectedFailure
    def test_add_user_form_renders(self):
        """/admin/accounts/user/add/ raises AttributeError on Django 2.2.

        `UserAdmin.get_form` swaps in `AdminAddUserForm`, a plain `forms.Form`;
        `ModelAdmin._changeform_view` then reads `form.instance`, which only
        ModelForms have. Flip to a normal test once the add form is a ModelForm
        (or `add_view` is overridden).
        """
        self.assertEqual(self.client.get('/admin/accounts/user/add/').status_code, 200)

    def test_non_staff_member_cannot_enter_admin(self):
        self.client.logout()
        self.client.force_login(make_user('member@example.com'))
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])
