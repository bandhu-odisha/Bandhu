"""Coverage-focused tests for bandhuapp/views.py: profile page, image admin actions,
user data export, annual reports upload, classic landing view, and _build_landing_data
branches not already exercised by test_landing.py / test_views_people.py.
"""
import json
import os
import unittest
from unittest import mock

from django.contrib import messages as django_messages
from django.test import TestCase, override_settings

from bandhuapp import views
from bandhuapp.models import (
    AboutSlide, AnnualReport, Contact, HeroSlide, HomePage, HomeVisitor,
    Photo, Video, Volunteer,
)
from bandhuapp.tests.support import (
    PASSWORD, TempMediaMixin, image_upload, make_admin, make_profile, make_user,
)


def get_messages(response):
    return [str(m) for m in django_messages.get_messages(response.wsgi_request)]


class ClassicFileUrlTests(TestCase):
    def test_none_field_returns_none(self):
        self.assertIsNone(views._classic_file_url(None))

    def test_field_without_name_returns_none(self):
        field = mock.Mock()
        field.name = ''
        self.assertIsNone(views._classic_file_url(field))

    def test_field_url_value_error_returns_none(self):
        field = mock.Mock()
        field.name = 'something.png'
        type(field).url = mock.PropertyMock(side_effect=ValueError)
        self.assertIsNone(views._classic_file_url(field))

    def test_field_with_valid_url(self):
        field = mock.Mock()
        field.name = 'something.png'
        field.url = '/media/something.png'
        self.assertEqual(views._classic_file_url(field), '/media/something.png')


class ClassicIndexViewTests(TempMediaMixin, TestCase):
    def test_member_without_profile_is_redirected_with_message(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.get('/classic/')
        self.assertRedirects(response, '/profile/', fetch_redirect_response=False)
        self.assertIn('Complete your Profile first.', get_messages(response))

    def test_get_does_not_increment_visitor_count(self):
        home = HomePage.objects.create(banner_image='tests/banner.gif', visitors_count=0)
        self.client.get('/classic/')
        self.client.get('/classic/')
        home.refresh_from_db()
        self.assertEqual(home.visitors_count, 0)

    def test_visit_beacon_increments_by_one(self):
        home = HomePage.objects.create(banner_image='tests/banner.gif', visitors_count=0)
        response = self.client.post('/api/visit/')
        self.assertEqual(response.status_code, 200)
        home.refresh_from_db()
        self.assertEqual(home.visitors_count, 1)

    def test_anonymous_renders_with_context(self):
        response = self.client.get('/classic/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('initiatives', response.context)
        self.assertIn('recent_events', response.context)


class ProfilePageTests(TempMediaMixin, TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_get_first_time_shows_empty_form(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['first_time'])

    def test_get_existing_profile_shows_filled_form(self):
        member = make_user()
        make_profile(member)
        self.client.force_login(member)
        response = self.client.get('/profile/')
        self.assertFalse(response.context['first_time'])
        self.assertEqual(response.context['profile'].first_name, 'Test')

    def test_post_missing_required_fields_shows_errors_and_repopulates(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.post('/profile/', {
            'first_name': 'Ann',
            # last_name missing and other required fields missing
        })
        self.assertEqual(response.status_code, 200)
        joined = ''.join(get_messages(response))
        self.assertIn('Last name is required.', joined)
        self.assertIn('Gender is required.', joined)
        self.assertEqual(response.context['profile'].first_name, 'Ann')

    def test_post_first_time_without_photo_requires_profile_pic(self):
        member = make_user()
        self.client.force_login(member)
        data = {
            'first_name': 'Ann', 'last_name': 'Roy', 'gender': 'F', 'dob': '1990-01-01',
            'profession': 'Teacher', 'contact_no': '9998887777', 'street_address1': 'Street 1',
            'city': 'Cuttack', 'state': 'Odisha', 'pincode': '753001',
        }
        response = self.client.post('/profile/', data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Profile picture is required.', ''.join(get_messages(response)))

    @mock.patch('bandhuapp.views.SendGridAPIClient')
    def test_post_first_time_valid_creates_profile_and_logs_out(self, mock_sg_client):
        mock_sg_client.return_value.send.return_value = mock.Mock(
            status_code=202, body=b'', headers={}
        )
        member = make_user()
        self.client.force_login(member)
        data = {
            'first_name': 'ann', 'last_name': 'roy', 'gender': 'F', 'dob': '1990-01-01',
            'profession': 'teacher', 'contact_no': '9998887777', 'street_address1': 'street 1',
            'city': 'cuttack', 'state': 'odisha', 'pincode': '753001',
            'profile_pic': image_upload(),
        }
        response = self.client.post('/profile/', data)
        self.assertRedirects(response, '/accounts/activated/', fetch_redirect_response=False)
        from bandhuapp.models import Profile
        profile = Profile.objects.get(user=member)
        self.assertEqual(profile.first_name, 'Ann')  # proper_case applied
        self.assertEqual(profile.city, 'Cuttack')
        mock_sg_client.return_value.send.assert_called_once()
        # user should be logged out
        response2 = self.client.get('/profile/')
        self.assertEqual(response2.status_code, 302)
        self.assertIn('/accounts/login/', response2.url)

    @mock.patch('bandhuapp.views.SendGridAPIClient')
    def test_post_first_time_sendgrid_exception_is_swallowed(self, mock_sg_client):
        mock_sg_client.side_effect = Exception('boom')
        member = make_user()
        self.client.force_login(member)
        data = {
            'first_name': 'ann', 'last_name': 'roy', 'gender': 'F', 'dob': '1990-01-01',
            'profession': 'teacher', 'contact_no': '9998887777', 'street_address1': 'street 1',
            'city': 'cuttack', 'state': 'odisha', 'pincode': '753001',
            'profile_pic': image_upload(),
        }
        with self.assertLogs('bandhuapp.views', level='ERROR'):
            response = self.client.post('/profile/', data)
        # Even though SendGrid raised, the view should still redirect to account_activated.
        self.assertRedirects(response, '/accounts/activated/', fetch_redirect_response=False)

    @mock.patch('bandhuapp.views.SendGridAPIClient')
    def test_post_not_first_time_updates_and_redirects_to_profile(self, mock_sg_client):
        member = make_user()
        make_profile(member, first_name='Old', profile_pic=image_upload('old.gif'))
        self.client.force_login(member)
        data = {
            'first_name': 'new', 'last_name': 'name', 'gender': 'M', 'dob': '1991-02-02',
            'profession': 'engineer', 'contact_no': '9990001111', 'street_address1': 'addr',
            'city': 'city', 'state': 'state', 'pincode': '750001',
            'profile_pic': image_upload('new.gif'),
        }
        response = self.client.post('/profile/', data)
        self.assertRedirects(response, '/profile/', fetch_redirect_response=False)
        mock_sg_client.assert_not_called()
        from bandhuapp.models import Profile
        profile = Profile.objects.get(user=member)
        self.assertEqual(profile.first_name, 'New')


class AddImageTests(TempMediaMixin, TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.post('/photos/add_image/', {})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_regular_member_denied(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.post('/photos/add_image/', {})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_admin_can_add_image(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.post('/photos/add_image/', {
            'image': image_upload(),
            'caption': 'A nice photo',
            'tags': ['nature', 'garden'],
        })
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        photo = Photo.objects.get(caption='A nice photo')
        self.assertTrue(photo.approved)
        self.assertEqual(photo.tags, 'nature garden ')
        self.assertIn('Image added successfully!', get_messages(response))

    def test_get_just_redirects_home(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.get('/photos/add_image/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class ApproveImageTests(TempMediaMixin, TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.post('/photos/approve_image/', {})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_approve_marks_photo_approved(self):
        member = make_user()
        self.client.force_login(member)
        photo = Photo.objects.create(picture=image_upload(), caption='x', approved=False)
        response = self.client.post('/photos/approve_image/', {
            'image': str(photo.pk), 'status': 'approve',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {'response': 'approved'})
        photo.refresh_from_db()
        self.assertTrue(photo.approved)

    def test_discard_deletes_photo(self):
        member = make_user()
        self.client.force_login(member)
        photo = Photo.objects.create(picture=image_upload(), caption='x', approved=False)
        pk = photo.pk
        response = self.client.post('/photos/approve_image/', {
            'image': str(pk), 'status': 'discard',
        })
        self.assertEqual(json.loads(response.content), {'response': 'discarded'})
        self.assertFalse(Photo.objects.filter(pk=pk).exists())

    def test_unknown_photo_is_404(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.post('/photos/approve_image/', {
            'image': '99999', 'status': 'approve',
        })
        self.assertEqual(response.status_code, 404)

    def test_get_just_redirects_home(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.get('/photos/approve_image/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)


class ExtractUserDataTests(TempMediaMixin, TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get('/user_profile_data/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_authenticated_user_generates_xlsx(self):
        os.makedirs(os.path.join(self.media_dir, 'sheets'), exist_ok=True)
        admin = make_admin()
        make_profile(admin, first_name='Site', last_name='Admin', pincode='751001')
        member = make_user('m2@example.com')
        make_profile(member, first_name='Reg', last_name='Member', pincode='751002')
        self.client.force_login(admin)
        response = self.client.get('/user_profile_data/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/sheets/user_profile_data.xlsx', response.url)
        file_path = os.path.join(self.media_dir, 'sheets', 'user_profile_data.xlsx')
        self.assertTrue(os.path.isfile(file_path))


class AnnualReportsUploadTests(TempMediaMixin, TestCase):
    def test_anonymous_redirected_to_login(self):
        response = self.client.get('/annual-reports/upload/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_regular_member_denied(self):
        member = make_user()
        self.client.force_login(member)
        response = self.client.get('/annual-reports/upload/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_get_non_ajax_redirects_to_home_contact(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.get('/annual-reports/upload/')
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)

    def test_get_ajax_returns_reports_json(self):
        admin = make_admin()
        self.client.force_login(admin)
        AnnualReport.objects.create(year=2023, external_url='https://drive.example/x')
        response = self.client.get('/annual-reports/upload/', {'format': 'json'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['reports']), 1)
        self.assertEqual(data['reports'][0]['year'], 2023)

    def test_post_create_valid_non_ajax(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.post('/annual-reports/upload/', {
            'year': 2024, 'title': '', 'external_url': 'https://drive.example/y',
            'is_published': 'on',
        })
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)
        report = AnnualReport.objects.get(year=2024)
        self.assertEqual(report.display_title(), 'Annual Report 2024')
        self.assertIn(f'Saved {report.display_title()}.', get_messages(response))

    def test_post_create_valid_ajax(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.post(
            '/annual-reports/upload/',
            {'year': 2025, 'external_url': 'https://drive.example/z', 'is_published': 'on'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['ok'])
        self.assertIn('reports', data)

    def test_post_invalid_form_non_ajax(self):
        admin = make_admin()
        self.client.force_login(admin)
        # No pdf_file and no external_url -> form.clean() raises ValidationError
        response = self.client.post('/annual-reports/upload/', {'year': 2026, 'is_published': 'on'})
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)
        self.assertIn('Could not save the report. Please check the form.', get_messages(response))
        self.assertFalse(AnnualReport.objects.filter(year=2026).exists())

    def test_post_invalid_form_ajax_returns_errors(self):
        admin = make_admin()
        self.client.force_login(admin)
        response = self.client.post(
            '/annual-reports/upload/',
            {'year': 2027, 'is_published': 'on'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['ok'])
        self.assertIn('__all__', data['errors'])

    def test_post_delete_non_ajax(self):
        admin = make_admin()
        self.client.force_login(admin)
        report = AnnualReport.objects.create(year=2020, external_url='https://drive.example/old')
        response = self.client.post('/annual-reports/upload/', {
            'action': 'delete', 'report_id': report.pk,
        })
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)
        self.assertFalse(AnnualReport.objects.filter(pk=report.pk).exists())

    def test_post_delete_ajax(self):
        admin = make_admin()
        self.client.force_login(admin)
        report = AnnualReport.objects.create(year=2021, external_url='https://drive.example/old2')
        response = self.client.post(
            '/annual-reports/upload/',
            {'action': 'delete', 'report_id': report.pk},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['ok'])
        self.assertFalse(AnnualReport.objects.filter(pk=report.pk).exists())

    def test_post_update_existing_report(self):
        admin = make_admin()
        self.client.force_login(admin)
        report = AnnualReport.objects.create(year=2022, external_url='https://drive.example/orig')
        response = self.client.post('/annual-reports/upload/', {
            'report_id': report.pk, 'year': 2022, 'title': 'Updated Title',
            'external_url': 'https://drive.example/updated', 'is_published': 'on',
        })
        self.assertRedirects(response, '/#contact', fetch_redirect_response=False)
        report.refresh_from_db()
        self.assertEqual(report.title, 'Updated Title')


@override_settings()
class BuildLandingDataBranchTests(TempMediaMixin, TestCase):
    """Exercise branches inside _build_landing_data not covered by test_landing.py."""

    def get_data(self):
        response = self.client.get('/api/landing/')
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)

    def _photo_with_file(self, relative_path, **fields):
        """Create a Photo whose `picture` points at a real file under MEDIA_ROOT,
        so views._build_landing_data's file_url() resolves a URL for it."""
        full_path = os.path.join(self.media_dir, *relative_path.split('/'))
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'wb') as fh:
            from bandhuapp.tests.support import TINY_GIF
            fh.write(TINY_GIF)
        photo = Photo(approved=True, **fields)
        photo.picture.name = relative_path
        photo.save()
        return photo

    def test_photos_filtering_and_dedup(self):
        # main_page/initiatives -> skipped
        self._photo_with_file('main_page/initiatives/skip.gif', caption='skip')
        # profile_photos -> goes to profile_photos list
        self._photo_with_file('profile_photos/p1.gif', caption='profile')
        # about-slide in name -> skipped
        self._photo_with_file('bandhuapp/gallery/about-slide-x.gif', caption='slide')
        # not under bandhuapp/gallery -> skipped
        self._photo_with_file('random/other.gif', caption='other')
        # valid gallery photo
        self._photo_with_file('bandhuapp/gallery/nice_ab1234.gif', caption='nice', tags='a,b')
        # exact same picture URL re-used under a second Photo row -> deduped by URL
        self._photo_with_file('bandhuapp/gallery/nice_ab1234.gif', caption='nice_dupe')
        data = self.get_data()
        captions = {p['caption'] for p in data['photos']}
        # only one of the two same-URL photos survives (whichever sorts first by -created)
        self.assertEqual(len(captions & {'nice', 'nice_dupe'}), 1)
        self.assertNotIn('skip', captions)
        self.assertNotIn('other', captions)
        self.assertNotIn('slide', captions)
        profile_captions = {p['caption'] for p in data['profile_photos']}
        self.assertIn('profile', profile_captions)
        # tags parsed from comma/space separated string, on whichever of the pair survived
        survivor = next(p for p in data['photos'] if p['caption'] in {'nice', 'nice_dupe'})
        if survivor['caption'] == 'nice':
            self.assertEqual(survivor['tags'], ['a', 'b'])

    def test_stem_dedup_strips_hash_suffix(self):
        # Regression: the stem regex used to be `_[a-z0-9]{6,7}(?=\.)`, run on the basename
        # *after* os.path.splitext had removed the extension. The lookahead demanded a literal
        # '.' that can no longer be there, so the substitution never matched and two gallery
        # photos differing only by Django's random re-upload suffix both reached the payload.
        # Anchored on $ instead, so only one of the pair survives.
        self._photo_with_file('bandhuapp/gallery/nice_ab1234.gif', caption='nice')
        self._photo_with_file('bandhuapp/gallery/nice_cd5678.gif', caption='nice2')
        data = self.get_data()
        captions = {p['caption'] for p in data['photos']}
        self.assertEqual(len(captions & {'nice', 'nice2'}), 1)

    def test_photo_without_usable_url_is_skipped(self):
        # picture points at a file that does not exist on disk and has no static fallback
        # -> file_url() returns None -> pic_data['picture'] falsy -> skipped.
        photo = Photo(approved=True, caption='ghost')
        photo.picture.name = 'bandhuapp/gallery/ghost-missing.gif'
        photo.save()
        data = self.get_data()
        captions = {p['caption'] for p in data['photos']}
        self.assertNotIn('ghost', captions)

    def test_gallery_photo_gets_a_real_webp_thumbnail(self):
        # Home page load-time spec, Step 2: easy_thumbnails must actually generate
        # a WebP thumbnail for a real image file, not just wire up config that
        # silently no-ops. Regression for the easy-thumbnails 2.6 / Pillow 10
        # `Image.ANTIALIAS` incompatibility (bandhu/settings.py has the shim).
        self._photo_with_file('bandhuapp/gallery/responsive_test.gif', caption='responsive')
        data = self.get_data()
        photo = next(p for p in data['photos'] if p['caption'] == 'responsive')
        responsive = photo['picture_responsive']
        self.assertTrue(responsive['src'].endswith('.webp'))
        self.assertIn('480w', responsive['srcset'])
        self.assertIn('960w', responsive['srcset'])
        self.assertIn('1600w', responsive['srcset'])
        self.assertGreater(responsive['width'], 0)
        self.assertGreater(responsive['height'], 0)

    def test_thumbnail_dimensions_are_process_cached(self):
        # Regression: `ThumbnailFile.width`/`.height` (easy_thumbnails) query the
        # DB and, absent THUMBNAIL_CACHE_DIMENSIONS, open the thumbnail file from
        # storage on *every* access. `responsive_image` (bandhuapp/helpers.py)
        # wraps that in a process cache so a repeat request for the same image
        # costs neither a query nor a file read. Without the cache, this would
        # scale per-photo per-request -- exactly the class of cost Steps 1 and 3
        # of the home-page load-time spec removed.
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        from bandhuapp.helpers import responsive_image

        photo = self._photo_with_file('bandhuapp/gallery/dims_cache_test.gif', caption='dims')
        first = responsive_image(photo.picture)
        self.assertIsNotNone(first)
        with CaptureQueriesContext(connection) as ctx:
            second = responsive_image(photo.picture)
        self.assertEqual(second, first)
        thumbnail_queries = [q for q in ctx.captured_queries if 'thumbnail' in q['sql'].lower()]
        self.assertEqual(thumbnail_queries, [])

    def test_about_slides_custom_overrides_defaults(self):
        AboutSlide.objects.create(image=image_upload('custom-slide.gif'), caption='Custom caption', sort_order=1)
        data = self.get_data()
        self.assertEqual(len(data['about_slides']), 1)
        self.assertEqual(data['about_slides'][0]['caption'], 'Custom caption')

    def test_gallery_tagline_present_when_gallery_exists(self):
        from bandhuapp.models import Gallery
        Gallery.objects.create(tagline='Our Gallery')
        data = self.get_data()
        self.assertEqual(data.get('gallery_tagline'), 'Our Gallery')

    def test_hero_slides_serialized(self):
        HeroSlide.objects.create(title='T1', subtitle='S1', image=image_upload('hero1.gif'), sort_order=1)
        data = self.get_data()
        self.assertEqual(len(data['hero_slides']), 1)
        self.assertEqual(data['hero_slides'][0]['title'], 'T1')

    def test_about_and_volunteer_and_content_present(self):
        from bandhuapp.models import AboutUs
        AboutUs.objects.create(tagline='Tag', desc='Desc')
        Volunteer.objects.create(title='Vol', tagline='Join us')
        HomePage.objects.create(banner_image=image_upload('banner.gif'), visitors_count=0)
        data = self.get_data()
        self.assertEqual(data['about'], {'tagline': 'Tag', 'desc': 'Desc'})
        self.assertEqual(data['volunteer'], {'title': 'Vol', 'tagline': 'Join us'})
        self.assertIsNotNone(data['content'])
        self.assertEqual(data['content']['visitors_count'], 0)

    def test_contact_present(self):
        Contact.objects.create(
            address='addr', contact_no='123', email='a@b.com',
            facebook_link='fb', twitter_link='tw',
        )
        data = self.get_data()
        self.assertEqual(data['contact']['email'], 'a@b.com')

    def test_home_visitor_serialized(self):
        HomeVisitor.objects.create(
            name='Vis', occupation='Doctor', place='Cuttack', avatar='man',
            quote='Great work', is_published=True,
        )
        HomeVisitor.objects.create(
            name='Hidden', occupation='X', place='Y', avatar='man',
            quote='Q', is_published=False,
        )
        data = self.get_data()
        names = {v['name'] for v in data['visitors']}
        self.assertIn('Vis', names)
        self.assertNotIn('Hidden', names)

    def test_video_youtube_id_extraction_variants(self):
        Video.objects.create(title='Embed', script='https://www.youtube.com/embed/abcdefghijk')
        Video.objects.create(title='Watch', script='https://www.youtube.com/watch?v=zyxwvutsrqp')
        Video.objects.create(title='Short', script='https://youtu.be/1234567890a')
        Video.objects.create(title='NoMatch', script='not a youtube link at all')
        data = self.get_data()
        by_title = {v['title']: v for v in data['videos']}
        self.assertEqual(by_title['Embed']['video_id'], 'abcdefghijk')
        self.assertEqual(by_title['Watch']['video_id'], 'zyxwvutsrqp')
        self.assertEqual(by_title['Short']['video_id'], '1234567890a')
        self.assertIsNone(by_title['NoMatch']['video_id'])

    def test_video_duration_non_string_is_stringified(self):
        video = Video.objects.create(title='Dur', script='https://youtu.be/1234567890a', duration='5:42')
        data = self.get_data()
        by_title = {v['title']: v for v in data['videos']}
        self.assertEqual(by_title['Dur']['duration'], '5:42')

    def test_video_empty_duration_is_none(self):
        Video.objects.create(title='NoDur', script='https://youtu.be/1234567890a', duration='')
        data = self.get_data()
        by_title = {v['title']: v for v in data['videos']}
        self.assertIsNone(by_title['NoDur']['duration'])

    def test_recent_activities_serialized_with_dates(self):
        from bandhuapp.models import RecentActivity
        RecentActivity.objects.create(
            title='Camp', description='desc',
            start_date='2024-01-01', end_date='2024-01-02',
        )
        data = self.get_data()
        activity = next(a for a in data['recent_activities'] if a['title'] == 'Camp')
        self.assertEqual(activity['start_date'], '2024-01-01')
        self.assertEqual(activity['end_date'], '2024-01-02')
