"""Shared regression tests for the unified initiative program pattern.

Each clone app (prasantaraktadan, patriotism, sevavrata) subclasses
`InitiativeProgramTestsMixin` with its own `program_key` and `models` module so
the publish logic in `bandhuapp/initiative_program_year.py` is exercised against
every registered program.
"""

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django.urls import reverse

from bandhuapp import initiative_program_year as ipy
from bandhuapp.tests.support import (
    TempMediaMixin,
    file_upload,
    image_upload,
    make_admin,
    make_user,
)

LOGIN_URL = '/accounts/login/'


class InitiativeProgramTestsMixin(TempMediaMixin):
    program_key = None  # set by subclass
    models = None  # set by subclass (the app's models module)

    # ----- helpers -----------------------------------------------------

    @property
    def meta(self):
        return ipy.PROGRAMS[self.program_key]

    def url(self, name, **kwargs):
        return reverse(f'{self.program_key}:{name}', kwargs=kwargs or None)

    def detail_url(self, entry):
        return reverse(self.meta['detail_url'], kwargs={'slug': entry.slug})

    def make_entry(self, name='Camp 2024', slug='camp-2024', **extra):
        return self.models.Ashram.objects.create(
            name=name,
            locality='Cuttack',
            description='Year entry',
            address='Bandhu campus',
            image='tests/hero.gif',
            slug=slug,
            **extra,
        )

    def make_category(self, name='General'):
        return self.models.ActivityCategory.objects.get_or_create(name=name)[0]

    def request_for(self, user=None):
        request = RequestFactory().get('/')
        request.user = user or AnonymousUser()
        return request

    def login_admin(self):
        admin = make_admin(f'{self.program_key}-admin@example.com')
        self.client.force_login(admin)
        return admin

    def login_member(self):
        member = make_user(f'{self.program_key}-member@example.com')
        self.client.force_login(member)
        return member

    # ----- entry_has_public_content / maybe_publish_entry ------------------

    def test_new_entry_is_draft_without_content(self):
        entry = self.make_entry()
        self.assertFalse(entry.is_published)
        self.assertFalse(ipy.entry_has_public_content(entry, self.models))
        ipy.maybe_publish_entry(entry, self.models)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_each_public_content_kind_publishes_entry(self):
        m = self.models
        cases = {
            'reports_text': lambda e: m.Ashram.objects.filter(pk=e.pk).update(reports='See report'),
            'report_link': lambda e: m.AshramReportLink.objects.create(ashram=e, title='Drive', url='https://example.com/r'),
            'report_file': lambda e: m.AshramReportFile.objects.create(ashram=e, file=file_upload(), title='PDF'),
            'invitation': lambda e: m.AshramInvitationLetter.objects.create(ashram=e, file=file_upload('invite.pdf')),
            'activity': lambda e: m.Activity.objects.create(ashram=e, category=self.make_category(), name='Drive', description='d'),
            'event': lambda e: m.Event.objects.create(ashram=e, name='Ev', description='d', thumb=image_upload(), date='2024-01-15'),
            'approved_gallery_photo': lambda e: m.Photo.objects.create(ashram=e, picture=image_upload(), approved=True),
        }
        for index, (label, add_content) in enumerate(cases.items()):
            with self.subTest(content=label):
                entry = self.make_entry(name=f'Entry {index}', slug=f'entry-{index}')
                add_content(entry)
                entry.refresh_from_db()
                self.assertTrue(ipy.entry_has_public_content(entry, self.models))
                ipy.maybe_publish_entry(entry, self.models)
                entry.refresh_from_db()
                self.assertTrue(entry.is_published)

    def test_unapproved_gallery_photo_does_not_publish(self):
        entry = self.make_entry()
        self.models.Photo.objects.create(ashram=entry, picture=image_upload(), approved=False)
        self.assertFalse(ipy.entry_has_public_content(entry, self.models))
        ipy.maybe_publish_entry(entry, self.models)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_blank_reports_text_is_not_public_content(self):
        entry = self.make_entry(reports='   \n')
        self.assertFalse(ipy.entry_has_public_content(entry, self.models))

    # ----- reconcile_publish_states ----------------------------------------

    def test_reconcile_unpublishes_entry_that_lost_its_content(self):
        entry = self.make_entry(is_published=True)
        ipy.reconcile_publish_states(self.models)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_reconcile_publishes_draft_that_has_content(self):
        entry = self.make_entry(reports='Report text')
        self.assertFalse(entry.is_published)
        ipy.reconcile_publish_states(self.models)
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    # ----- get_visible_entries / index gallery -----------------------------

    def test_get_visible_entries_hides_drafts_from_public_only(self):
        published = self.make_entry(name='Published', slug='published', reports='r', is_published=True)
        draft = self.make_entry(name='Draft', slug='draft')
        admin = make_admin(f'{self.program_key}-vis@example.com')

        public = list(ipy.get_visible_entries(self.request_for(), self.models))
        self.assertEqual(public, [published])

        for_admin = list(ipy.get_visible_entries(self.request_for(admin), self.models))
        self.assertEqual({e.pk for e in for_admin}, {published.pk, draft.pk})

    def test_index_gallery_hides_draft_photos_from_public(self):
        draft = self.make_entry(name='Draft', slug='draft')
        photo = self.models.Photo.objects.create(ashram=draft, picture=image_upload(), approved=True)
        # Photo approval alone publishes the entry via maybe_publish; force draft to test the filter.
        self.models.Ashram.objects.filter(pk=draft.pk).update(is_published=False)

        public_ctx = ipy.build_index_gallery_context(self.request_for(), self.program_key, self.models)
        self.assertFalse(public_ctx['show_gallery'])
        self.assertNotIn(photo, list(public_ctx['photos']))

        admin = make_admin(f'{self.program_key}-gal@example.com')
        admin_ctx = ipy.build_index_gallery_context(self.request_for(admin), self.program_key, self.models)
        self.assertTrue(admin_ctx['show_gallery'])
        self.assertIn(photo, list(admin_ctx['photos']))

    # ----- list + detail pages -------------------------------------------

    def test_list_page_shows_only_published_entries_to_public(self):
        published = self.make_entry(name='Published', slug='published', reports='r')
        draft = self.make_entry(name='Draft', slug='draft')

        response = self.client.get(reverse(self.meta['list_url']))
        self.assertEqual(response.status_code, 200)
        slugs = [e.slug for e in response.context['ashrams']]
        self.assertEqual(slugs, [published.slug])
        self.assertFalse(response.context['check_admin'])

        self.login_admin()
        response = self.client.get(reverse(self.meta['list_url']))
        self.assertEqual(response.status_code, 200)
        slugs = {e.slug for e in response.context['ashrams']}
        self.assertEqual(slugs, {published.slug, draft.slug})
        self.assertTrue(response.context['check_admin'])

    def test_detail_of_draft_is_404_for_public_and_visible_to_admin(self):
        draft = self.make_entry(name='Draft', slug='draft')

        self.assertEqual(self.client.get(self.detail_url(draft)).status_code, 404)

        self.login_admin()
        response = self.client.get(self.detail_url(draft))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['entry_is_draft'])
        self.assertEqual(response.context['program_key'], self.program_key)

    def test_detail_of_published_entry_renders_for_public(self):
        entry = self.make_entry(reports='Report text')
        other = self.make_entry(name='Other', slug='other', reports='r')
        self.make_entry(name='Hidden draft', slug='hidden-draft')
        category = self.make_category('Camps')
        activity = self.models.Activity.objects.create(ashram=entry, category=category, name='Drive', description='d')
        self.models.Photo.objects.create(ashram=entry, picture=image_upload(), activity=activity, approved=True)
        self.models.Photo.objects.create(ashram=entry, picture=image_upload(), activity=activity, approved=False)
        self.models.Photo.objects.create(ashram=entry, picture=image_upload(), approved=True)
        self.models.Event.objects.create(ashram=entry, name='Ev', description='d', thumb=image_upload(), date='2024-01-15')

        response = self.client.get(self.detail_url(entry))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['entry_is_draft'])
        self.assertEqual(response.context['hero_title'], f'{entry.name} - {entry.locality}')
        self.assertEqual([e.slug for e in response.context['other_entries']], [other.slug])
        self.assertTrue(response.context['has_activities'])
        self.assertTrue(response.context['has_events'])
        self.assertTrue(response.context['show_gallery'])
        # Public visitors only see approved activity photos.
        activity_row = list(response.context['activities'])[0]
        self.assertEqual(len(activity_row.photo_set.all()), 1)

    def test_hero_title_omits_missing_locality(self):
        entry = self.make_entry(reports='r')
        self.models.Ashram.objects.filter(pk=entry.pk).update(locality='  ')
        response = self.client.get(self.detail_url(entry))
        self.assertEqual(response.context['hero_title'], entry.name)

    def test_detail_unknown_slug_is_404(self):
        self.assertEqual(self.client.get(reverse(self.meta['detail_url'], kwargs={'slug': 'missing'})).status_code, 404)

    # ----- admin-only view factories ---------------------------------------

    def test_admin_only_views_redirect_anonymous_to_login(self):
        entry = self.make_entry()
        link = self.models.AshramReportLink.objects.create(ashram=entry, title='t', url='https://example.com')
        report = self.models.AshramReportFile.objects.create(ashram=entry, file=file_upload())
        targets = [
            self.url('UploadReportFile', slug=entry.slug),
            self.url('AddReportLink', slug=entry.slug),
            self.url('DeleteReportFile', pk=report.pk),
            self.url('DeleteReportLink', pk=link.pk),
            self.url('UploadInvitation', slug=entry.slug),
            self.url('DeleteInvitation', slug=entry.slug),
            self.url('UpdateDescription', slug=entry.slug),
        ]
        for target in targets:
            with self.subTest(url=target):
                response = self.client.post(target, {})
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response['Location'].startswith(LOGIN_URL))
        self.assertTrue(self.models.AshramReportLink.objects.filter(pk=link.pk).exists())
        self.assertTrue(self.models.AshramReportFile.objects.filter(pk=report.pk).exists())

    def test_non_admin_member_cannot_use_admin_only_views(self):
        entry = self.make_entry()
        self.login_member()
        response = self.client.post(
            self.url('AddReportLink', slug=entry.slug),
            {'title': 'Drive', 'url': 'https://example.com/r'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(LOGIN_URL))
        self.assertEqual(self.models.AshramReportLink.objects.count(), 0)

    def test_admin_get_on_post_only_views_redirects_to_detail(self):
        entry = self.make_entry()
        self.login_admin()
        for name in ('UploadReportFile', 'AddReportLink', 'UploadInvitation', 'UpdateDescription'):
            with self.subTest(view=name):
                response = self.client.get(self.url(name, slug=entry.slug))
                self.assertRedirects(response, self.detail_url(entry), fetch_redirect_response=False)
        for name in ('AddToGallery', 'AddActivityCategory', 'CreateActivity'):
            with self.subTest(view=name):
                self.assertRedirects(self.client.get(self.url(name)), '/', fetch_redirect_response=False)
        event_view = self.meta['create_event_url'].split(':')[1]
        self.assertRedirects(self.client.get(self.url(event_view)), '/', fetch_redirect_response=False)
        self.assertRedirects(self.client.get(reverse(self.meta['approval_url'])), '/', fetch_redirect_response=False)
        self.assertRedirects(
            self.client.get(reverse(self.meta['create_ashram_url'])),
            reverse(self.meta['list_url']), fetch_redirect_response=False,
        )

    def test_admin_upload_report_file_publishes_entry(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(
            self.url('UploadReportFile', slug=entry.slug),
            {'report_file': file_upload('annual.pdf'), 'title': ''},
        )
        self.assertRedirects(response, self.detail_url(entry) + '#reports', fetch_redirect_response=False)
        report = self.models.AshramReportFile.objects.get(ashram=entry)
        self.assertEqual(report.title, 'annual.pdf')
        self.assertEqual(str(report), 'annual.pdf')
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    def test_upload_report_file_without_file_keeps_draft(self):
        entry = self.make_entry()
        self.login_admin()
        self.client.post(self.url('UploadReportFile', slug=entry.slug), {})
        self.assertEqual(self.models.AshramReportFile.objects.count(), 0)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_add_report_link_requires_title_and_url(self):
        entry = self.make_entry()
        self.login_admin()
        self.client.post(self.url('AddReportLink', slug=entry.slug), {'title': 'Only title'})
        self.assertEqual(self.models.AshramReportLink.objects.count(), 0)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_add_and_delete_report_link(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(
            self.url('AddReportLink', slug=entry.slug),
            {'title': 'Drive', 'url': 'https://example.com/r'},
        )
        self.assertRedirects(response, self.detail_url(entry) + '#reports', fetch_redirect_response=False)
        link = self.models.AshramReportLink.objects.get(ashram=entry)
        self.assertEqual(str(link), 'Drive')
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

        response = self.client.post(self.url('DeleteReportLink', pk=link.pk))
        self.assertRedirects(response, self.detail_url(entry) + '#reports', fetch_redirect_response=False)
        self.assertFalse(self.models.AshramReportLink.objects.filter(pk=link.pk).exists())

    def test_delete_report_file_removes_row(self):
        entry = self.make_entry()
        report = self.models.AshramReportFile.objects.create(ashram=entry, file=file_upload())
        self.login_admin()
        self.client.post(self.url('DeleteReportFile', pk=report.pk))
        self.assertFalse(self.models.AshramReportFile.objects.filter(pk=report.pk).exists())

    def test_upload_and_delete_invitation_letter(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(
            self.url('UploadInvitation', slug=entry.slug),
            {'invitation_file': file_upload('invite.pdf')},
        )
        self.assertRedirects(response, self.detail_url(entry) + '#invitation', fetch_redirect_response=False)
        letter = self.models.AshramInvitationLetter.objects.get(ashram=entry)
        self.assertEqual(str(letter), f'Invitation — {entry.name}')
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

        # Re-upload replaces the single letter rather than adding a second one.
        self.client.post(self.url('UploadInvitation', slug=entry.slug), {'invitation_file': file_upload('v2.pdf')})
        self.assertEqual(self.models.AshramInvitationLetter.objects.filter(ashram=entry).count(), 1)

        self.client.post(self.url('DeleteInvitation', slug=entry.slug))
        self.assertFalse(self.models.AshramInvitationLetter.objects.filter(ashram=entry).exists())

    def test_upload_invitation_without_file_reports_error(self):
        entry = self.make_entry()
        self.login_admin()
        self.client.post(self.url('UploadInvitation', slug=entry.slug), {})
        self.assertFalse(self.models.AshramInvitationLetter.objects.filter(ashram=entry).exists())
        self.client.post(self.url('DeleteInvitation', slug=entry.slug))  # nothing to delete: no error

    def test_update_description(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(self.url('UpdateDescription', slug=entry.slug), {'description': 'New text'})
        self.assertRedirects(response, self.detail_url(entry) + '#description', fetch_redirect_response=False)
        entry.refresh_from_db()
        self.assertEqual(entry.description, 'New text')
        # Description alone is not public content, so the entry stays a draft.
        self.assertFalse(entry.is_published)

    # ----- login-required content views -----------------------------------

    def test_create_activity_publishes_entry_and_approves_admin_photos(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(self.url('CreateActivity'), {
            'slug': entry.slug,
            'activity_name': 'Blood drive',
            'category_name': 'Camps',
            'description': 'd',
            'activity_images': [image_upload('a.gif')],
        })
        self.assertRedirects(response, self.detail_url(entry) + '#activities', fetch_redirect_response=False)
        activity = self.models.Activity.objects.get(ashram=entry)
        self.assertEqual(activity.category.name, 'Camps')
        self.assertEqual(str(activity), f'{entry.name} - Blood drive (Camps)')
        photo = self.models.Photo.objects.get(activity=activity)
        self.assertTrue(photo.approved)
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    def test_create_activity_with_existing_category_id(self):
        entry = self.make_entry()
        category = self.make_category('Existing')
        self.login_admin()
        self.client.post(self.url('CreateActivity'), {
            'slug': entry.slug, 'activity_name': 'Drive', 'category': category.pk,
            'activity_images': [image_upload('a.gif')],
        })
        self.assertEqual(self.models.Activity.objects.get(ashram=entry).category, category)

    def test_create_activity_validation(self):
        entry = self.make_entry()
        self.login_admin()
        self.client.post(self.url('CreateActivity'), {'slug': entry.slug, 'activity_name': 'No image'})
        self.client.post(self.url('CreateActivity'), {'slug': entry.slug})
        response = self.client.post(self.url('CreateActivity'), {'activity_name': 'No slug'})
        self.assertRedirects(response, reverse(self.meta['list_url']), fetch_redirect_response=False)
        self.assertEqual(self.models.Activity.objects.count(), 0)

    def test_member_gallery_upload_is_unapproved_and_keeps_draft(self):
        entry = self.make_entry()
        self.login_member()
        response = self.client.post(self.url('AddToGallery'), {
            'slug': entry.slug,
            'gallery_images': [image_upload('g.gif')],
        })
        self.assertRedirects(response, self.detail_url(entry) + '#gallery', fetch_redirect_response=False)
        photo = self.models.Photo.objects.get(ashram=entry)
        self.assertFalse(photo.approved)
        entry.refresh_from_db()
        self.assertFalse(entry.is_published)

    def test_admin_gallery_upload_is_approved_and_publishes(self):
        entry = self.make_entry()
        self.login_admin()
        self.client.post(self.url('AddToGallery'), {
            'slug': entry.slug,
            'gallery_images': [image_upload('g1.gif'), image_upload('g2.gif'), image_upload('g1.gif')],
        })
        # Duplicate (name, size) uploads within one request are skipped.
        self.assertEqual(self.models.Photo.objects.filter(ashram=entry, approved=True).count(), 2)
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    def test_gallery_upload_validation(self):
        entry = self.make_entry()
        self.login_admin()
        self.assertRedirects(self.client.post(self.url('AddToGallery'), {}), reverse(self.meta['list_url']), fetch_redirect_response=False)
        self.client.post(self.url('AddToGallery'), {'slug': entry.slug})
        self.assertEqual(self.models.Photo.objects.count(), 0)

    def test_add_activity_category_is_program_wide_and_idempotent(self):
        entry = self.make_entry()
        self.login_admin()
        for _ in range(2):
            response = self.client.post(self.url('AddActivityCategory'), {'slug': entry.slug, 'name': 'Camps'})
            self.assertRedirects(response, self.detail_url(entry) + '#activities', fetch_redirect_response=False)
        self.assertEqual(self.models.ActivityCategory.objects.filter(name='Camps').count(), 1)
        self.assertEqual(str(self.models.ActivityCategory.objects.get(name='Camps')), 'Camps')
        response = self.client.post(self.url('AddActivityCategory'), {'name': ''})
        self.assertRedirects(response, reverse(self.meta['list_url']), fetch_redirect_response=False)

    def test_create_event_publishes_entry(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(self.url(self.meta['create_event_url'].split(':')[1]), {
            'slug': entry.slug,
            'event_name': 'Camp day',
            'event_date': '2024-02-10',
            'description': 'd',
            'event_thumb': image_upload('t.gif'),
        })
        self.assertRedirects(response, self.detail_url(entry) + '#events', fetch_redirect_response=False)
        event = self.models.Event.objects.get(ashram=entry)
        self.assertEqual(str(event), f'{entry.name} - Camp day')
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    def test_create_event_requires_all_fields(self):
        entry = self.make_entry()
        self.login_admin()
        view = self.url(self.meta['create_event_url'].split(':')[1])
        response = self.client.post(view, {'slug': entry.slug, 'event_name': 'Missing thumb', 'event_date': '2024-02-10'})
        self.assertRedirects(response, self.detail_url(entry) + '#activities', fetch_redirect_response=False)
        response = self.client.post(view, {'event_name': 'No slug'})
        self.assertRedirects(response, reverse(self.meta['list_url']), fetch_redirect_response=False)
        self.assertEqual(self.models.Event.objects.count(), 0)

    def test_admin_approval_approves_photo_and_publishes(self):
        entry = self.make_entry()
        photo = self.models.Photo.objects.create(ashram=entry, picture=image_upload(), approved=False)
        self.login_admin()
        response = self.client.post(reverse(self.meta['approval_url']), {
            self.meta['approval_field']: entry.slug,
            'image': photo.pk,
            'status': 'approve',
        })
        self.assertRedirects(response, self.detail_url(entry) + '#gallery', fetch_redirect_response=False)
        photo.refresh_from_db()
        self.assertTrue(photo.approved)
        entry.refresh_from_db()
        self.assertTrue(entry.is_published)

    def test_admin_approval_ajax_returns_json_and_discard_deletes(self):
        entry = self.make_entry()
        photo = self.models.Photo.objects.create(ashram=entry, picture=image_upload(), approved=False)
        self.login_admin()
        response = self.client.post(
            reverse(self.meta['approval_url']),
            {self.meta['approval_field']: entry.slug, 'image': photo.pk, 'status': 'discard'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertFalse(self.models.Photo.objects.filter(pk=photo.pk).exists())

    def test_create_entry_view_creates_draft(self):
        self.login_admin()
        response = self.client.post(reverse(self.meta['create_ashram_url']), {
            'name': 'New Camp',
            'locality': 'Puri',
            'description': 'd',
            'address': 'a',
            'image': image_upload('hero.gif'),
        })
        entry = self.models.Ashram.objects.get(name='New Camp')
        self.assertEqual(entry.slug, 'new-camp-puri')
        self.assertEqual(str(entry), 'New Camp - Puri')
        self.assertFalse(entry.is_published)
        self.assertRedirects(response, self.detail_url(entry), fetch_redirect_response=False)

    def test_create_entry_rejects_duplicate_name_and_locality(self):
        self.make_entry(name='New Camp', slug='new-camp-cuttack')
        self.login_admin()
        response = self.client.post(reverse(self.meta['create_ashram_url']), {
            'name': 'New Camp',
            'locality': 'Cuttack',
            'description': 'd',
            'address': 'a',
            'image': image_upload('hero.gif'),
        })
        self.assertRedirects(response, reverse(self.meta['list_url']), fetch_redirect_response=False)
        self.assertEqual(self.models.Ashram.objects.filter(name='New Camp').count(), 1)

    def test_create_entry_requires_login(self):
        response = self.client.post(reverse(self.meta['create_ashram_url']), {})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(LOGIN_URL))

    # ----- meetings / attendees (legacy views kept per app) -----------------

    def test_add_meeting_and_attendees(self):
        entry = self.make_entry()
        self.login_admin()
        response = self.client.post(self.url('AddMeeting'), {
            'slug': entry.slug, 'topic': 'Planning', 'agenda': 'a', 'schedule': '2024-01-05 10:00',
            'location': 'Office', 'minutes': file_upload('minutes.pdf'),
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(f'/detail/{entry.slug}/'))
        meeting = self.models.Meeting.objects.get(ashram=entry)
        self.assertIn('Planning', str(meeting))

        response = self.client.post(self.url('AddAttendee'), {
            'schedule': '2024-01-05 10:00', 'topic': 'Planning', 'slug': entry.slug,
            'name': 'Guest', 'email': 'g@example.com', 'contact_no': '123', 'attendes': '',
        })
        self.assertEqual(response.status_code, 302)
        attendee = self.models.Attendee.objects.get(meeting=meeting)
        self.assertEqual(attendee.name, 'Guest')
        self.assertIn('Guest', str(attendee))

        from bandhuapp.tests.support import make_profile
        member = make_user(f'{self.program_key}-att@example.com')
        make_profile(member, first_name='Asha', last_name='Rao', contact_no='555')
        self.client.post(self.url('AddAttendee'), {
            'schedule': '2024-01-05 10:00', 'topic': 'Planning', 'slug': entry.slug,
            'name': '', 'attendes': f'{member.email},nobody@example.com',
        })
        by_profile = self.models.Attendee.objects.get(profile__user=member)
        self.assertEqual(by_profile.name, 'Asha Rao')
        self.assertEqual(by_profile.email, member.email)
        self.assertEqual(by_profile.contact_no, '555')

        for name in ('AddMeeting', 'AddAttendee'):
            self.assertRedirects(self.client.get(self.url(name)), '/', fetch_redirect_response=False)
