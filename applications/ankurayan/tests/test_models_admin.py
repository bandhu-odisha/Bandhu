"""Regression tests for Ankurayan models, admin registrations and template tags."""

from datetime import date

from django.test import TestCase
from django.urls import reverse

from bandhuapp.tests.support import TempMediaMixin, file_upload, image_upload, make_user
from applications.ankurayan.admin import AnkurayanAdmin, GuestAdmin, GuestNoteAdmin
from applications.ankurayan.models import (
    Activity, ActivityCategory, Ankurayan, AnkurayanInvitationLetter,
    AnkurayanPublicationFile, AnkurayanReportFile, Guest, GuestNote, HomePage,
    Participant, Photo,
)
from applications.ankurayan.templatetags.ankurayan_tags import guest_avatar_url


def make_ankurayan(year=2024):
    return Ankurayan.objects.create(
        year=year, title=f'Ankurayan {year}', theme='T', description='D',
        start_date=date(year, 12, 17), end_date=date(year, 12, 19),
        logo='ankurayan/logo/Logo.jpg', slug=str(year),
    )


class ModelStrTests(TestCase):
    def setUp(self):
        self.ankurayan = make_ankurayan()

    def test_str_representations(self):
        category = ActivityCategory.objects.create(ankurayan=self.ankurayan, name='Art')
        activity = Activity.objects.create(
            category=category, name='Painting', description='d', date=date(2024, 12, 17))
        participant = Participant.objects.create(
            ankurayan=self.ankurayan, name='Kid', school_class='5', address='a', contact_no='1')
        guest = Guest.objects.create(ankurayan=self.ankurayan, name='G', profession='Judge')
        note = GuestNote.objects.create(guest=guest, note='n')
        photo = Photo.objects.create(ankurayan=self.ankurayan, picture='ankurayan/2024/x.jpg')
        report = AnkurayanReportFile.objects.create(
            ankurayan=self.ankurayan, file='ankurayan/reports/2024/r.pdf', title='')
        publication = AnkurayanPublicationFile.objects.create(
            ankurayan=self.ankurayan, file='ankurayan/publications/2024/p.pdf', title='Pub')
        letter = AnkurayanInvitationLetter.objects.create(
            ankurayan=self.ankurayan, file='ankurayan/invitation_letters/i.pdf')
        home = HomePage.objects.create(tagline='t', description='d')

        self.assertEqual(str(self.ankurayan), 'Ankurayan 2024')
        self.assertEqual(str(category), '2024 - Art')
        self.assertEqual(str(activity), '2024 - Painting (Art)')
        self.assertEqual(str(participant), '2024 - Kid')
        self.assertEqual(str(guest), '2024 - G (Judge)')
        self.assertEqual(str(note), f'Note for G ({note.created_at.date()})')
        self.assertEqual(str(photo), '2024')
        self.assertEqual(str(report), 'ankurayan/reports/2024/r.pdf')
        self.assertEqual(str(publication), 'Pub')
        self.assertEqual(str(letter), 'Invitation letter — Ankurayan 2024')
        self.assertEqual(str(home), 'Ankurayan Home Page Content')

    def test_guest_ordering_by_sort_order_then_name(self):
        Guest.objects.create(ankurayan=self.ankurayan, name='Zed', profession='p', sort_order=0)
        Guest.objects.create(ankurayan=self.ankurayan, name='Amy', profession='p', sort_order=1)
        Guest.objects.create(ankurayan=self.ankurayan, name='Bob', profession='p', sort_order=0)
        self.assertEqual(list(Guest.objects.values_list('name', flat=True)), ['Bob', 'Zed', 'Amy'])

    def test_deleting_ankurayan_cascades_children(self):
        Guest.objects.create(ankurayan=self.ankurayan, name='G', profession='p')
        Photo.objects.create(ankurayan=self.ankurayan, picture='ankurayan/2024/x.jpg')
        self.ankurayan.delete()
        self.assertEqual(Guest.objects.count(), 0)
        self.assertEqual(Photo.objects.count(), 0)


class TemplateTagTests(TempMediaMixin, TestCase):
    def test_guest_avatar_url(self):
        ankurayan = make_ankurayan()
        man = Guest.objects.create(ankurayan=ankurayan, name='M', profession='p', avatar='man')
        woman = Guest.objects.create(ankurayan=ankurayan, name='W', profession='p', avatar='woman')
        with_photo = Guest.objects.create(
            ankurayan=ankurayan, name='P', profession='p', photo=image_upload('face.gif'))
        self.assertEqual(guest_avatar_url(man), '/static/img/man.png')
        self.assertEqual(guest_avatar_url(woman), '/static/img/woman.png')
        self.assertTrue(guest_avatar_url(with_photo).startswith('/media/ankurayan/guests/face'))


class AdminTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.superuser = make_user('root@example.com', is_admin=True, is_staff=True,
                                   is_superuser=True, auth=True)
        self.client.force_login(self.superuser)
        self.ankurayan = make_ankurayan()

    def test_changelists_render(self):
        category = ActivityCategory.objects.create(ankurayan=self.ankurayan, name='Art')
        Activity.objects.create(category=category, name='A', description='d', date=date(2024, 12, 17))
        Participant.objects.create(
            ankurayan=self.ankurayan, name='Kid', school_class='5', address='a', contact_no='1')
        guest = Guest.objects.create(ankurayan=self.ankurayan, name='G', profession='p', quote='q' * 60)
        GuestNote.objects.create(guest=guest, note='n' * 70)
        Photo.objects.create(ankurayan=self.ankurayan, picture='ankurayan/2024/x.jpg')
        AnkurayanReportFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='R')
        AnkurayanPublicationFile.objects.create(ankurayan=self.ankurayan, file=file_upload(), title='P')
        AnkurayanInvitationLetter.objects.create(ankurayan=self.ankurayan, file=file_upload('i.pdf'))
        HomePage.objects.create(tagline='t', description='d')
        for model in ('ankurayan', 'activitycategory', 'activity', 'participant', 'guest',
                      'guestnote', 'photo', 'ankurayanreportfile', 'ankurayanpublicationfile',
                      'ankurayaninvitationletter', 'homepage'):
            url = reverse(f'admin:ankurayan_{model}_changelist')
            self.assertEqual(self.client.get(url).status_code, 200, model)
        self.assertEqual(self.client.get(
            reverse('admin:ankurayan_activitycategory_changelist') + '?q=Art').status_code, 200)
        self.assertEqual(self.client.get(
            reverse('admin:ankurayan_ankurayaninvitationletter_add')).status_code, 200)
        # HomePage is a singleton: add is blocked once one exists
        self.assertEqual(self.client.get(reverse('admin:ankurayan_homepage_add')).status_code, 403)

    def test_preview_helpers(self):
        guest = Guest.objects.create(ankurayan=self.ankurayan, name='G', profession='p')
        admin_obj = GuestAdmin(Guest, None)
        self.assertEqual(admin_obj.quote_preview(guest), '—')
        guest.quote = 'short'
        self.assertEqual(admin_obj.quote_preview(guest), 'short')
        guest.quote = 'x' * 51
        self.assertEqual(admin_obj.quote_preview(guest), 'x' * 50 + '…')

        note_admin = GuestNoteAdmin(GuestNote, None)
        note = GuestNote(guest=guest, note='  ')
        self.assertEqual(note_admin.note_preview(note), '—')
        note.note = 'y' * 61
        self.assertEqual(note_admin.note_preview(note), 'y' * 60 + '…')
        note.note = 'fine'
        self.assertEqual(note_admin.note_preview(note), 'fine')

    def test_response_add_redirects_to_detail_when_requested(self):
        data = {
            'year': '2025', 'title': 'Ankurayan 2025', 'theme': 'T', 'slug': '2025',
            'start_date': '2025-12-17', 'end_date': '2025-12-19', 'logo': image_upload(),
            'description': 'D', 'reports': '', 'publications': '', 'visitors': '',
            'image_caption_en': '', 'image_caption_or': '',
        }
        add_url = reverse('admin:ankurayan_ankurayan_add')
        response = self.client.post(add_url + '?next=ankurayan_details', data)
        self.assertRedirects(response, '/ankurayan/detail/2025/', fetch_redirect_response=False)
        self.assertTrue(Ankurayan.objects.filter(year=2025).exists())

        data.update({'year': '2026', 'slug': '2026', 'logo': image_upload()})
        response = self.client.post(add_url, data)
        self.assertRedirects(response, reverse('admin:ankurayan_ankurayan_changelist'),
                             fetch_redirect_response=False)
