"""Sanskar / Swaraj / Swabalamban pillar home pages."""

from django.test import TestCase

from bandhuapp import pillar_pages
from bandhuapp.models import SanskarHomePage, SwabalambanHomePage, SwarajHomePage
from bandhuapp.tests.support import TempMediaMixin, make_admin


class PillarPageTests(TempMediaMixin, TestCase):
    def test_pages_render_with_no_rows(self):
        for path, title in (('/sanskar/', 'Sanskar'), ('/swaraj/', 'Swaraj'), ('/swabalamban/', 'Swabalamban')):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['page_title'], title)
                self.assertEqual(response.context['tagline'], '')
                self.assertEqual(response.context['images'], [])

    def test_sanskar_uses_row_copy_and_default_captions(self):
        SanskarHomePage.objects.create(tagline='Values first', description='<b>Body</b>')
        response = self.client.get('/sanskar/')
        self.assertEqual(response.context['tagline'], 'Values first')
        self.assertEqual(response.context['desc'], '<b>Body</b>')
        self.assertEqual(response.context['image_caption_en'], pillar_pages.DEFAULT_SANSKAR_IMAGE_CAPTION_EN)
        self.assertEqual(response.context['image_caption_or'], pillar_pages.DEFAULT_SANSKAR_IMAGE_CAPTION_OR)
        self.assertEqual([link['name'] for link in response.context['related_links']], ['Anandakendra', 'Ankurayan'])

    def test_sanskar_custom_caption_overrides_default(self):
        SanskarHomePage.objects.create(tagline='t', image_caption_en='"Custom"')
        self.assertEqual(self.client.get('/sanskar/').context['image_caption_en'], '"Custom"')

    def test_swaraj_caption_falls_back_from_image_to_text_to_default(self):
        page = SwarajHomePage.objects.create(tagline='t')
        self.assertEqual(pillar_pages.build_swaraj_context()['image_caption_en'], pillar_pages.DEFAULT_SWARAJ_TEXT_CAPTION_EN)
        page.text_caption_en = '"Text card"'
        page.save()
        self.assertEqual(pillar_pages.build_swaraj_context()['image_caption_en'], '"Text card"')
        page.image_caption_en = '"Image"'
        page.save()
        self.assertEqual(pillar_pages.build_swaraj_context()['image_caption_en'], '"Image"')

    def test_swabalamban_products_heading_and_admin_flag(self):
        SwabalambanHomePage.objects.create(tagline='t', products_heading='', whatsapp_number='+91 99999')
        response = self.client.get('/swabalamban/')
        self.assertEqual(response.context['products_heading'], 'Quality produce from our Swabalamban initiative.')
        self.assertEqual(response.context['whatsapp_number'], '+91 99999')
        self.assertFalse(response.context['check_admin'])

        self.client.force_login(make_admin())
        self.assertTrue(self.client.get('/swabalamban/').context['check_admin'])

    def test_missing_hero_falls_back_to_static_image(self):
        ctx = pillar_pages.build_sanskar_context(related_links=[])
        self.assertIsNone(ctx['pillar_hero_image'])
        self.assertTrue(ctx['pillar_hero_url'].endswith('img/our_mission.jpg'))

    def test_mission_card_payload_shape(self):
        SanskarHomePage.objects.create(tagline='Sanskar tag', description='Sanskar body')
        payload = pillar_pages.mission_card_payload(lambda field: None)
        self.assertEqual(payload['sanskar_tagline'], 'Sanskar tag')
        self.assertEqual(payload['sanskar_desc'], 'Sanskar body')
        self.assertEqual(payload['sanskar_images'], [])
        self.assertEqual(payload['swaraj_tagline'], '')
