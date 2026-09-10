from django.test import TestCase

from bandhuapp.tests.support import TempMediaMixin, make_admin


class IndexSmokeTests(TempMediaMixin, TestCase):
    def test_index_renders_for_public_and_admin(self):
        self.assertEqual(self.client.get('/ankurayan/').status_code, 200)
        self.client.force_login(make_admin())
        self.assertEqual(self.client.get('/ankurayan/').status_code, 200)
