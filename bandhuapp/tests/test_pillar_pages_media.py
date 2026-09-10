"""Pillar pages with real media on disk: hero selection, stale-file pruning, mission cards."""

import os

from django.test import TestCase

from bandhuapp import pillar_pages
from bandhuapp.models import SanskarHomePage, SanskarHomePhoto, SwarajHomePage, SwarajHomePhoto
from bandhuapp.tests.support import TempMediaMixin, image_upload


class PillarMediaTests(TempMediaMixin, TestCase):
    def test_collage_photo_is_preferred_as_sanskar_hero_when_no_hero_image(self):
        page = SanskarHomePage.objects.create(tagline='t')
        plain = SanskarHomePhoto.objects.create(page=page, picture=image_upload('pimg2.gif'), sort_order=0)
        collage = SanskarHomePhoto.objects.create(page=page, picture=image_upload('collage.gif'), sort_order=1)
        ctx = pillar_pages.build_sanskar_context(related_links=[])
        self.assertEqual(ctx['pillar_hero_image'], collage.picture)
        self.assertTrue(ctx['pillar_hero_url'].startswith('/media/'))
        # The hero is excluded from the gallery; the other photo remains.
        self.assertEqual([img.name for img in ctx['images']], [plain.picture.name])

    def test_first_available_photo_is_hero_when_nothing_matches_collage(self):
        page = SwarajHomePage.objects.create(tagline='t')
        first = SwarajHomePhoto.objects.create(page=page, picture=image_upload('a.gif'), sort_order=0)
        SwarajHomePhoto.objects.create(page=page, picture=image_upload('b.gif'), sort_order=1)
        ctx = pillar_pages.build_swaraj_context()
        self.assertEqual(ctx['pillar_hero_image'], first.picture)
        self.assertEqual(len(ctx['images']), 1)

    def test_explicit_hero_image_wins_over_gallery(self):
        page = SwarajHomePage.objects.create(tagline='t', hero_image=image_upload('hero.gif'))
        SwarajHomePhoto.objects.create(page=page, picture=image_upload('a.gif'))
        ctx = pillar_pages.build_swaraj_context()
        self.assertEqual(ctx['pillar_hero_image'], page.hero_image)
        self.assertEqual(len(ctx['images']), 1)

    def test_stale_media_paths_are_pruned(self):
        page = SanskarHomePage.objects.create(tagline='t', hero_image='bandhuapp/pillar_heroes/missing.gif')
        SanskarHomePhoto.objects.create(page=page, picture='bandhuapp/sanskar/missing.gif')
        kept = SanskarHomePhoto.objects.create(page=page, picture=image_upload('kept.gif'))
        ctx = pillar_pages.build_sanskar_context(related_links=[])
        page.refresh_from_db()
        self.assertFalse(page.hero_image)
        self.assertEqual(list(SanskarHomePhoto.objects.filter(page=page)), [kept])
        self.assertEqual(ctx['pillar_hero_image'], kept.picture)

    def test_deleted_file_on_disk_falls_back_to_static_hero(self):
        page = SwarajHomePage.objects.create(tagline='t', hero_image=image_upload('hero.gif'))
        os.remove(os.path.join(self.media_dir, page.hero_image.name))
        ctx = pillar_pages.build_swaraj_context()
        self.assertIsNone(ctx['pillar_hero_image'])
        self.assertTrue(ctx['pillar_hero_url'].endswith('img/our_mission1.jpg'))

    def test_mission_card_uses_hero_then_first_gallery_photo(self):
        page = SanskarHomePage.objects.create(tagline='Sanskar', description='d')
        photo = SanskarHomePhoto.objects.create(page=page, picture=image_upload('gallery.gif'))

        with_urls = pillar_pages.mission_card_payload(lambda field: field.url if field else None)
        self.assertEqual(with_urls['sanskar_images'], [{'picture': photo.picture.url}])

        # file_url may refuse the hero (e.g. missing on disk) but accept a gallery row.
        def only_gallery(field):
            return None if field == photo.picture else 'x'
        page.hero_image = image_upload('hero.gif')
        page.save()
        payload = pillar_pages.mission_card_payload(only_gallery)
        self.assertEqual(payload['sanskar_images'], [{'picture': 'x'}])

        def nothing(field):
            return None
        self.assertEqual(pillar_pages.mission_card_payload(nothing)['sanskar_images'], [])
