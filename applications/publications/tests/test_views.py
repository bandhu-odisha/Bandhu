"""Publications: listing, detail, download, models and admin."""

import os
from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from applications.publications.models import HomePage, Publication
from bandhuapp.tests.support import (
    TempMediaMixin, file_upload, image_upload, make_admin, make_profile, make_user,
)


def make_publication(slug='report', title='Report', created=None, media=None, thumb=None, **fields):
    created = created or timezone.make_aware(datetime(2024, 1, 1, 12, 0))
    return Publication.objects.create(
        slug=slug, title=title, description='d', created=created,
        thumb=thumb if thumb is not None else 'publications/thumb/t.gif',
        media=media if media is not None else 'publications/m.pdf',
        **fields,
    )


class PublicationListTests(TempMediaMixin, TestCase):
    def test_index_lists_visible_publications_newest_first(self):
        old = make_publication('old', created=timezone.make_aware(datetime(2020, 1, 1)))
        new = make_publication('new', created=timezone.make_aware(datetime(2023, 1, 1)))
        make_publication('hidden', is_visible=False)
        home = HomePage.objects.create(tagline='Read us', description='desc')
        response = self.client.get('/publications/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['publications']), [new, old])
        self.assertEqual(response.context['content'], home)
        self.assertEqual(str(home), 'Publications Home Page Content')


class PublicationDetailTests(TempMediaMixin, TestCase):
    def test_detail_renders_with_media_author_and_domain(self):
        author = make_profile(make_user('author@example.com'), first_name='Asha', last_name='Writer')
        publication = make_publication(
            'paika', title='<b>Paika</b> 2024', media=file_upload('paika.pdf'), thumb=image_upload(), by=author,
        )
        response = self.client.get('/publications/paika/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['publication'], publication)
        self.assertEqual(response.context['domain'], 'testserver')
        self.assertIsNone(response.context['content'])
        self.assertContains(response, 'PAIKA 2024')
        self.assertContains(response, 'Asha')
        self.assertContains(response, '/publications/paika/download/')
        self.assertEqual(str(publication), 'Paika 2024')

    def test_detail_without_media_shows_placeholder(self):
        make_publication('empty', media='')
        response = self.client.get('/publications/empty/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not available for download yet')

    def test_hidden_or_missing_detail_is_404(self):
        make_publication('hidden', is_visible=False)
        self.assertEqual(self.client.get('/publications/hidden/').status_code, 404)
        self.assertEqual(self.client.get('/publications/nope/').status_code, 404)


class PublicationDownloadTests(TempMediaMixin, TestCase):
    def test_download_serves_file_as_attachment(self):
        make_publication('paika', media=file_upload('paika.pdf', b'%PDF-1.4 payload'))
        response = self.client.get('/publications/paika/download/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('paika', response['Content-Disposition'])
        self.assertEqual(b''.join(response.streaming_content), b'%PDF-1.4 payload')

    def test_download_404_when_no_media_or_file_missing_on_disk(self):
        make_publication('nomedia', media='')
        self.assertEqual(self.client.get('/publications/nomedia/download/').status_code, 404)

        publication = make_publication('gone', media=file_upload('gone.pdf'))
        os.remove(os.path.join(self.media_dir, publication.media.name))
        self.assertEqual(self.client.get('/publications/gone/download/').status_code, 404)

    def test_download_404_for_hidden_publication(self):
        make_publication('hidden', media=file_upload(), is_visible=False)
        self.assertEqual(self.client.get('/publications/hidden/download/').status_code, 404)


class PublicationAdminTests(TempMediaMixin, TestCase):
    def test_admin_pages_render(self):
        make_publication('one', title='<i>One</i>')
        self.client.force_login(make_admin())
        response = self.client.get('/admin/publications/publication/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'One')
        self.assertEqual(self.client.get('/admin/publications/publication/add/').status_code, 200)
        self.assertEqual(self.client.get('/admin/publications/homepage/').status_code, 200)
