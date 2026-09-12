from django.test import TestCase
from django.urls import reverse

from applications.sevavrata import models
from bandhuapp.tests.initiative_program_support import InitiativeProgramTestsMixin
from bandhuapp.tests.support import image_upload


class SevavrataProgramTests(InitiativeProgramTestsMixin, TestCase):
    program_key = 'sevavrata'
    models = models

    def test_create_entry_stores_schedule_dates(self):
        self.login_admin()
        self.client.post(reverse(self.meta['create_ashram_url']), {
            'name': 'Seva 2025',
            'locality': 'Puri',
            'description': 'd',
            'address': 'a',
            'image': image_upload('hero.gif'),
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
        })
        entry = models.Ashram.objects.get(name='Seva 2025')
        self.assertEqual(str(entry.start_date), '2025-01-01')
        self.assertEqual(str(entry.end_date), '2025-01-31')

    def test_program_declares_entry_schedule(self):
        entry = self.make_entry(reports='r', is_published=True)
        response = self.client.get(self.detail_url(entry))
        self.assertTrue(response.context['program_has_entry_schedule'])
