"""bandhuapp.helpers: image helpers, text case, YouTube duration, people-card logic."""

import io
from types import SimpleNamespace
from unittest import mock

from django.test import TestCase

from bandhuapp import helpers
from bandhuapp.models import Designation, DesignationRole, PeoplesDesignation, Photo, Staff
from bandhuapp.tests.support import TempMediaMixin, image_upload, make_profile, make_user


class _FakeResponse(io.BytesIO):
    """urlopen() context manager returning fixed HTML bytes."""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _urlopen_returning(html):
    return mock.patch(
        'bandhuapp.helpers.urllib.request.urlopen',
        return_value=_FakeResponse(html.encode('utf-8')),
    )


# --------------------------------------------------------------------------- images

class ImageHelperTests(TempMediaMixin, TestCase):
    def _photo(self, name='photo.gif'):
        return Photo.objects.create(picture=image_upload(name), approved=True)

    def test_image_field_available_false_for_empty_or_missing(self):
        self.assertFalse(helpers.image_field_available(None))
        photo = Photo(picture='')
        self.assertFalse(helpers.image_field_available(photo.picture))
        missing = Photo(picture='bandhuapp/gallery/does-not-exist.gif')
        self.assertFalse(helpers.image_field_available(missing.picture))

    def test_image_field_available_swallows_storage_errors(self):
        field = SimpleNamespace(name='x.gif', storage=mock.Mock())
        field.storage.exists.side_effect = OSError('disk gone')
        self.assertFalse(helpers.image_field_available(field))

    def test_image_field_url_only_when_file_exists(self):
        photo = self._photo()
        self.assertTrue(helpers.image_field_url(photo.picture).startswith('/media/'))
        photo.picture.storage.delete(photo.picture.name)
        self.assertIsNone(helpers.image_field_url(photo.picture))

    def test_image_field_url_swallows_url_errors(self):
        class BadUrl:
            name = 'x.gif'
            storage = mock.Mock(exists=mock.Mock(return_value=True))

            @property
            def url(self):
                raise ValueError('no url')

        self.assertIsNone(helpers.image_field_url(BadUrl()))

    def test_clear_stale_image_field(self):
        photo = self._photo()
        # File present -> nothing changes.
        self.assertFalse(helpers.clear_stale_image_field(photo, 'picture'))
        # Empty field -> nothing to clear.
        self.assertFalse(helpers.clear_stale_image_field(Photo(picture=''), 'picture'))
        # File gone -> DB path cleared and persisted.
        photo.picture.storage.delete(photo.picture.name)
        self.assertTrue(helpers.clear_stale_image_field(photo, 'picture'))
        photo.refresh_from_db()
        self.assertEqual(photo.picture.name, '')

    def test_prune_stale_pillar_photos_deletes_only_missing_files(self):
        keep = self._photo('keep.gif')
        gone = self._photo('gone.gif')
        gone.picture.storage.delete(gone.picture.name)
        Photo.objects.create(picture='', approved=True)  # empty name, untouched
        removed = helpers.prune_stale_pillar_photos(Photo.objects.all())
        self.assertEqual(removed, 1)
        self.assertTrue(Photo.objects.filter(pk=keep.pk).exists())
        self.assertFalse(Photo.objects.filter(pk=gone.pk).exists())

    def test_pillar_gallery_images_filters_and_dedupes(self):
        a = self._photo('a.gif')
        b = self._photo('b.gif')
        gone = self._photo('gone.gif')
        gone.picture.storage.delete(gone.picture.name)
        rows = [a, b, gone, Photo(picture=''), a]
        images = helpers.pillar_gallery_images(rows)
        self.assertEqual([img.name for img in images], [a.picture.name, b.picture.name])

    def test_pillar_gallery_images_accepts_raw_fields_and_excludes_hero(self):
        a = self._photo('a.gif')
        b = self._photo('b.gif')
        images = helpers.pillar_gallery_images([a.picture, b.picture], exclude_picture=a.picture)
        self.assertEqual([img.name for img in images], [b.picture.name])
        self.assertEqual(helpers.pillar_gallery_images(None), [])


# --------------------------------------------------------------------------- text

class ProperCaseTests(TestCase):
    def test_none_and_non_string_pass_through(self):
        self.assertIsNone(helpers.proper_case(None))
        self.assertEqual(helpers.proper_case(42), 42)

    def test_blank_returns_empty(self):
        self.assertEqual(helpers.proper_case('   '), '')

    def test_words_are_capitalised_and_whitespace_collapsed(self):
        self.assertEqual(helpers.proper_case('  hELLO   wORLD '), 'Hello World')

    def test_punctuation_is_preserved_around_core(self):
        self.assertEqual(helpers.proper_case('(social MEDIA), outreach!'), '(Social Media), Outreach!')
        self.assertEqual(helpers.proper_case('--- ok'), '--- Ok')


class HashAndDurationTests(TestCase):
    def test_create_hash_is_20_hex_chars(self):
        value = helpers._createHash()
        self.assertEqual(len(value), 20)
        int(value, 16)

    def test_format_duration_hms(self):
        self.assertEqual(helpers._format_duration_hms(0), '0:00')
        self.assertEqual(helpers._format_duration_hms(-5), '0:00')
        self.assertEqual(helpers._format_duration_hms(342), '5:42')
        self.assertEqual(helpers._format_duration_hms(3930), '1:05:30')


class FetchYoutubeDurationTests(TestCase):
    VIDEO_ID = 'dQw4w9WgXcQ'

    def test_rejects_invalid_ids_without_network(self):
        with mock.patch('bandhuapp.helpers.urllib.request.urlopen') as urlopen:
            self.assertIsNone(helpers.fetch_youtube_duration_formatted(None))
            self.assertIsNone(helpers.fetch_youtube_duration_formatted(123))
            self.assertIsNone(helpers.fetch_youtube_duration_formatted('short'))
        urlopen.assert_not_called()

    def test_quoted_length_seconds(self):
        with _urlopen_returning('x "lengthSeconds":"342" y') as urlopen:
            self.assertEqual(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID), '5:42')
        req = urlopen.call_args[0][0]
        self.assertEqual(req.full_url, f'https://www.youtube.com/watch?v={self.VIDEO_ID}')
        self.assertIn('Mozilla', req.get_header('User-agent'))

    def test_unquoted_length_seconds(self):
        with _urlopen_returning('"lengthSeconds":3930,'):
            self.assertEqual(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID), '1:05:30')

    def test_quoted_approx_duration_ms(self):
        with _urlopen_returning('"approxDurationMs":"65000"'):
            self.assertEqual(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID), '1:05')

    def test_unquoted_approx_duration_ms(self):
        with _urlopen_returning('"approxDurationMs":125999'):
            self.assertEqual(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID), '2:05')

    def test_no_match_returns_none(self):
        with _urlopen_returning('<html>nothing useful</html>'):
            self.assertIsNone(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID))

    def test_network_error_returns_none(self):
        with mock.patch('bandhuapp.helpers.urllib.request.urlopen', side_effect=OSError('down')):
            self.assertIsNone(helpers.fetch_youtube_duration_formatted(self.VIDEO_ID))


class EnrichVideoDurationsTests(TestCase):
    def test_returns_early_when_nothing_needed(self):
        items = [{'video_id': 'abc', 'duration': '1:00'}, {'video_id': '', 'duration': ''}]
        with mock.patch('bandhuapp.helpers.fetch_youtube_duration_formatted') as fetch:
            helpers.enrich_video_durations(items)
        fetch.assert_not_called()
        self.assertEqual(items[0]['duration'], '1:00')

    def test_fills_duration_and_tolerates_failures(self):
        def fake_fetch(video_id):
            if video_id == 'good_id_123':
                return '3:21'
            if video_id == 'boom_id_123':
                raise RuntimeError('boom')
            return None

        items = [
            {'video_id': 'good_id_123', 'duration': ''},
            {'video_id': 'boom_id_123', 'duration': ''},
            {'video_id': 'none_id_123'},
            {'video_id': 'have_id_123', 'duration': '9:99'},
        ]
        with mock.patch('bandhuapp.helpers.fetch_youtube_duration_formatted', side_effect=fake_fetch):
            helpers.enrich_video_durations(items, max_workers=2)
        self.assertEqual(items[0]['duration'], '3:21')
        self.assertEqual(items[1]['duration'], '')
        self.assertNotIn('duration', items[2])
        self.assertEqual(items[3]['duration'], '9:99')


# --------------------------------------------------------------------------- core team text

class CoreTeamTextTests(TestCase):
    def test_clean_core_team_profession_text(self):
        self.assertEqual(helpers.clean_core_team_profession_text(''), '')
        self.assertEqual(helpers.clean_core_team_profession_text(None), '')
        self.assertEqual(helpers.clean_core_team_profession_text(' Teacher (Core Team) '), 'Teacher')
        self.assertEqual(helpers.clean_core_team_profession_text('Teacher (core team member)'), 'Teacher')
        self.assertEqual(helpers.clean_core_team_profession_text('Teacher (Retired)'), 'Teacher (Retired)')

    def test_is_core_team_legacy_subtitle(self):
        self.assertTrue(helpers.is_core_team_legacy_subtitle('Upadestha'))
        self.assertTrue(helpers.is_core_team_legacy_subtitle('SAMPADAKA (Core Team)'))
        self.assertFalse(helpers.is_core_team_legacy_subtitle('Teacher'))
        self.assertFalse(helpers.is_core_team_legacy_subtitle(''))

    def test_card_lines_desc_is_legacy_role(self):
        self.assertEqual(helpers.core_team_card_lines('teacher', 'upadestha'), ['Upadestha', 'Teacher'])
        # Profession also a legacy label -> no occupation line.
        self.assertEqual(helpers.core_team_card_lines('sampadaka', 'upadestha'), ['Upadestha'])
        # Same text -> single line.
        self.assertEqual(helpers.core_team_card_lines('Upadestha', 'upadestha'), ['Upadestha'])

    def test_card_lines_profession_is_legacy_role(self):
        self.assertEqual(helpers.core_team_card_lines('sampadaka', 'engineer'), ['Sampadaka', 'Engineer'])
        self.assertEqual(helpers.core_team_card_lines('sampadaka', 'Sampadaka'), ['Sampadaka'])
        self.assertEqual(helpers.core_team_card_lines('sampadaka', ''), ['Sampadaka'])

    def test_card_lines_both_plain(self):
        self.assertEqual(helpers.core_team_card_lines('doctor', 'volunteer'), ['Volunteer', 'Doctor'])
        self.assertEqual(helpers.core_team_card_lines('doctor', 'DOCTOR'), ['Doctor'])

    def test_card_lines_only_one_source(self):
        self.assertEqual(helpers.core_team_card_lines('', 'farmer'), ['Farmer'])
        self.assertEqual(helpers.core_team_card_lines('farmer', ''), ['Farmer'])
        self.assertEqual(helpers.core_team_card_lines('', ''), [])
        self.assertEqual(helpers.core_team_card_lines(None, None, None), [])

    def test_card_lines_fall_back_to_staff_about(self):
        self.assertEqual(
            helpers.core_team_card_lines('', 'upadestha', 'retired banker'),
            ['Upadestha', 'Retired Banker'],
        )
        self.assertEqual(helpers.core_team_card_lines('', 'upadestha', 'core team'), ['Upadestha'])
        self.assertEqual(helpers.core_team_card_lines('', 'upadestha', 'UPADESTHA'), ['Upadestha'])

    def test_lines_to_position_occupation(self):
        self.assertEqual(helpers._lines_to_position_occupation(['A', 'B', 'C']), ('A', 'B'))
        self.assertEqual(helpers._lines_to_position_occupation(['Upadestha']), ('Upadestha', ''))
        self.assertEqual(helpers._lines_to_position_occupation(['Teacher']), ('', 'Teacher'))
        self.assertEqual(helpers._lines_to_position_occupation(['', None]), ('', ''))

    def test_people_card_namespace_applies_proper_case(self):
        card = helpers._people_card_namespace('staff', 'president', 'civil ENGINEER', '')
        self.assertEqual(card.staff, 'staff')
        self.assertEqual(card.position_line, 'President')
        self.assertEqual(card.occupation_line, 'Civil Engineer')
        self.assertEqual(card.groups_line, '')


# --------------------------------------------------------------------------- designations

class _PD(SimpleNamespace):
    """Lightweight stand-in for PeoplesDesignation in pure-python dedupe tests."""


class DedupeKeyTests(TestCase):
    def test_key_ignores_role_when_null(self):
        pd = _PD(staff_id=1, designation_id=2, role_id=None)
        self.assertEqual(helpers.peoples_designation_dedupe_key(pd), (1, 2))
        pd.role_id = 7
        self.assertEqual(helpers.peoples_designation_dedupe_key(pd), (1, 2, 7))

    def test_dedupe_keeps_best_rank_then_lowest_pk_and_sorts(self):
        d_office = SimpleNamespace(rank=1)
        d_core = SimpleNamespace(rank=2)
        rows = [
            _PD(pk=10, staff_id=1, designation_id=2, role_id=None, rank=5, designation=d_core),
            _PD(pk=11, staff_id=1, designation_id=2, role_id=None, rank=3, designation=d_core),  # better rank
            _PD(pk=12, staff_id=1, designation_id=2, role_id=None, rank=3, designation=d_core),  # tie -> higher pk loses
            _PD(pk=9, staff_id=1, designation_id=2, role_id=None, rank=3, designation=d_core),   # tie -> lower pk wins
            _PD(pk=20, staff_id=1, designation_id=1, role_id=4, rank=1, designation=d_office),
            _PD(pk=21, staff_id=1, designation_id=1, role_id=4, rank=1, designation=d_office),   # dup with role
        ]
        result = helpers.dedupe_peoples_designations(rows)
        self.assertEqual([r.pk for r in result], [20, 9])


class RemoveDuplicateDesignationsTests(TestCase):
    def setUp(self):
        self.staff = Staff.objects.create(profile=make_profile(make_user()), about='about')
        self.core = Designation.objects.create(title='Core Team', rank=2)
        self.office = Designation.objects.create(title='Office Bearers', rank=1)
        self.president = DesignationRole.objects.create(designation=self.office, title='President', rank=1)

    def _raw(self, designation, role=None, rank=9999):
        """Bypass model save/clean so duplicates can exist in the table."""
        PeoplesDesignation.objects.bulk_create([
            PeoplesDesignation(staff=self.staff, designation=designation, role=role, rank=rank)
        ])
        return PeoplesDesignation.objects.latest('pk')

    def test_returns_zero_when_clean(self):
        self._raw(self.core)
        self._raw(self.office, self.president)
        self.assertEqual(helpers.remove_duplicate_peoples_designations(), 0)
        self.assertEqual(PeoplesDesignation.objects.count(), 2)

    def test_removes_null_role_duplicates_keeping_lowest_pk(self):
        first = self._raw(self.core)
        self._raw(self.core)
        self._raw(self.core)
        self.assertEqual(helpers.remove_duplicate_peoples_designations(), 2)
        self.assertEqual(list(PeoplesDesignation.objects.values_list('pk', flat=True)), [first.pk])

    def test_removes_role_duplicates_and_null_role_orphans(self):
        # A true (staff, designation, role) duplicate with a non-null role is
        # blocked by the DB's unique_together constraint even via bulk_create
        # (SQLite treats repeated NULLs as distinct, but not repeated non-NULLs),
        # so only the null-role "orphan" branch is exercisable here.
        keep = self._raw(self.office, self.president)
        orphan = self._raw(self.office)  # null-role row for a designation that has a role row
        self.assertEqual(helpers.remove_duplicate_peoples_designations(), 1)
        remaining = set(PeoplesDesignation.objects.values_list('pk', flat=True))
        self.assertEqual(remaining, {keep.pk})
        self.assertNotIn(orphan.pk, remaining)


class PeopleCardFromAssignmentsTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.profile = make_profile(self.user, first_name='Asha', last_name='Das', profession='teacher')
        self.staff = Staff.objects.create(profile=self.profile, about='retired banker')
        self.core = Designation.objects.create(title='Core Team', rank=2)
        self.office = Designation.objects.create(title='Office Bearers', rank=1)
        self.other = Designation.objects.create(title='Advisors', rank=3)
        self.president = DesignationRole.objects.create(designation=self.office, title='president', rank=1)
        self.treasurer = DesignationRole.objects.create(designation=self.office, title='treasurer', rank=2)

    def _pd(self, designation, role=None, desc='', rank=9999):
        return PeoplesDesignation.objects.create(
            staff=self.staff, designation=designation, role=role, desc=desc, rank=rank
        )

    def test_single_office_bearer_row(self):
        pd = self._pd(self.office, self.president, desc='civil engineer')
        card = helpers.people_card_from_assignments([pd])
        self.assertIs(card.staff, self.staff)
        self.assertEqual(card.position_line, 'President')
        self.assertEqual(card.occupation_line, 'Civil Engineer')
        self.assertEqual(card.groups_line, '')

    def test_single_core_team_row_uses_profession_only(self):
        pd = self._pd(self.core)
        card = helpers.people_card_from_assignments([pd])
        self.assertEqual(card.position_line, '')
        self.assertEqual(card.occupation_line, 'Teacher')

    def test_single_plain_row_without_desc_or_profession(self):
        self.profile.profession = ''
        self.profile.save()
        pd = self._pd(self.other)
        card = helpers.people_card_from_assignments([pd])
        self.assertEqual((card.position_line, card.occupation_line), ('', ''))

    def test_office_and_core_team_combined(self):
        office_pd = self._pd(self.office, self.president, rank=1)
        core_pd = self._pd(self.core, desc='upadestha', rank=2)
        card = helpers.people_card_from_assignments([office_pd, core_pd])
        self.assertEqual(card.position_line, 'President')
        self.assertEqual(card.groups_line, 'Office Bearers · Core Team')
        # Core Team row supplies the occupation from the profile profession.
        self.assertEqual(card.occupation_line, 'Teacher')

    def test_two_office_roles_same_group_lists_roles(self):
        p1 = self._pd(self.office, self.president, desc='doctor', rank=1)
        p2 = self._pd(self.office, self.treasurer, rank=2)
        card = helpers.people_card_from_assignments([p1, p2])
        self.assertEqual(card.position_line, 'President · Treasurer')
        self.assertEqual(card.groups_line, 'President · Treasurer')
        self.assertEqual(card.occupation_line, 'Doctor')

    def test_no_office_roles_takes_first_display_line(self):
        core_pd = self._pd(self.core, desc='sampadaka', rank=1)
        other_pd = self._pd(self.other, desc='farmer', rank=2)
        card = helpers.people_card_from_assignments([core_pd, other_pd])
        self.assertEqual(card.position_line, 'Sampadaka')
        self.assertEqual(card.groups_line, 'Core Team · Advisors')
        # The loop doesn't break after the Core Team row sets an occupation;
        # the later plain "Advisors" row's own desc overwrites it since
        # 'Farmer' isn't yet in shown_occupation/shown_position.
        self.assertEqual(card.occupation_line, 'Farmer')

    def test_plain_rows_fall_back_to_profession_and_skip_shown_position(self):
        self.profile.profession = 'advisor'
        self.profile.save()
        a = self._pd(self.other, desc='advisor', rank=1)
        b = self._pd(self.office, self.president, rank=2)
        # position_line = 'President' (office role); 'Advisor' differs so becomes occupation.
        card = helpers.people_card_from_assignments([a, b])
        self.assertEqual(card.position_line, 'President')
        self.assertEqual(card.occupation_line, 'Advisor')

    def test_plain_rows_with_empty_desc_use_profile_profession(self):
        a = self._pd(self.other, rank=1)
        b = self._pd(self.office, self.treasurer, rank=2)
        card = helpers.people_card_from_assignments([a, b])
        self.assertEqual(card.position_line, 'Treasurer')
        self.assertEqual(card.occupation_line, 'Teacher')
