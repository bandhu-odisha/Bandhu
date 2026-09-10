"""Bandhughar (the original, non-unified initiative app)."""

import json

from django.test import TestCase

from applications.ashram.models import Ashram, Event, Photo
from bandhuapp.tests.support import TempMediaMixin, image_upload, make_admin, make_user


def make_ashram(name='Bandhughar One', locality='Cuttack', slug='bandhughar-one-cuttack'):
    return Ashram.objects.create(
        name=name, locality=locality, description='d', address='a', image='tests/hero.gif', slug=slug,
    )


class BandhugharViewTests(TempMediaMixin, TestCase):
    def test_index_lists_every_ashram(self):
        ashram = make_ashram()
        response = self.client.get('/bandhughar/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(ashram, list(response.context['ashrams']))

    def test_detail_renders_and_unknown_is_404(self):
        ashram = make_ashram()
        self.assertEqual(self.client.get(f'/bandhughar/detail/{ashram.slug}/').status_code, 200)
        self.assertEqual(self.client.get('/bandhughar/detail/missing/').status_code, 404)

    def test_create_requires_login(self):
        response = self.client.post('/bandhughar/new/', {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/accounts/login/'))

    def test_create_ashram_and_reject_duplicate(self):
        self.client.force_login(make_user())
        data = {'name': 'Ghar', 'locality': 'Puri', 'description': 'd', 'address': 'a', 'image': image_upload()}
        response = self.client.post('/bandhughar/new/', data)
        self.assertRedirects(response, '/bandhughar/detail/ghar-puri/', fetch_redirect_response=False)

        data['image'] = image_upload()
        response = self.client.post('/bandhughar/new/', data)
        self.assertRedirects(response, '/bandhughar/', fetch_redirect_response=False)
        self.assertEqual(Ashram.objects.filter(name='Ghar').count(), 1)

    def test_create_event(self):
        ashram = make_ashram()
        self.client.force_login(make_admin())
        response = self.client.post('/bandhughar/create/event/', {
            'slug': ashram.slug, 'event_name': 'Meet', 'event_date': '2024-03-01',
            'description': 'd', 'event_thumb': image_upload(),
        })
        self.assertRedirects(response, f'/bandhughar/detail/{ashram.slug}/', fetch_redirect_response=False)
        self.assertEqual(Event.objects.filter(ashram=ashram).count(), 1)

    def test_admin_approval_approves_or_discards(self):
        ashram = make_ashram()
        photo = Photo.objects.create(ashram=ashram, picture=image_upload(), approved=False)
        self.client.force_login(make_admin())
        response = self.client.post('/bandhughar/admin_approval/', {
            'ashram': ashram.slug, 'image': photo.pk, 'status': 'approve',
        })
        self.assertEqual(response.status_code, 200)
        photo.refresh_from_db()
        self.assertTrue(photo.approved)
        self.assertEqual(len(json.loads(json.loads(response.content))), 1)

        self.client.post('/bandhughar/admin_approval/', {'ashram': ashram.slug, 'image': photo.pk, 'status': 'discard'})
        self.assertFalse(Photo.objects.filter(pk=photo.pk).exists())
