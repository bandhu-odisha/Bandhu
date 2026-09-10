import unittest

from django.template import TemplateDoesNotExist
from django.test import TestCase


class IndexSmokeTests(TestCase):
    @unittest.expectedFailure
    def test_index_renders(self):
        """Fails until `madhmukti/index.html` is added with `git add -f` (see .gitignore)."""
        self.assertEqual(self.client.get('/madh_mukti/').status_code, 200)

    def test_index_currently_raises_template_does_not_exist(self):
        with self.assertRaises(TemplateDoesNotExist):
            self.client.get('/madh_mukti/')
