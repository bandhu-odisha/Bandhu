"""Coverage for bandhuapp.admin_forms and bandhuapp.annual_report_forms."""

from unittest import mock

from django.forms import inlineformset_factory
from django.test import TestCase

from bandhuapp.admin_forms import (
    AdminAddProfileForm,
    DesignationAdminForm,
    DesignationRoleAdminForm,
    PeoplesDesignationAdminForm,
    PeoplesDesignationInlineFormSet,
    RoleSelect,
    StaffExperienceAdminForm,
    StaffExperienceInlineForm,
    _save_experience_photo,
    create_profile_for_admin_user,
)
from bandhuapp.annual_report_forms import AnnualReportUploadForm
from bandhuapp.models import (
    AnnualReport,
    Designation,
    DesignationRole,
    PeoplesDesignation,
    Profile,
    Staff,
    StaffExperience,
)
from bandhuapp.tests.support import (
    PASSWORD,
    TempMediaMixin,
    file_upload,
    image_upload,
    make_admin,
    make_profile,
    make_user,
)


# --------------------------------------------------------------------------- ProperCaseTitleForm

class DesignationAdminFormTests(TestCase):
    def test_clean_title_proper_cases(self):
        form = DesignationAdminForm(data={'title': 'office bearers', 'rank': 1})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['title'], 'Office Bearers')

    def test_designation_role_form_proper_cases_title(self):
        designation = Designation.objects.create(title='Office Bearers', rank=1)
        form = DesignationRoleAdminForm(
            data={'designation': designation.pk, 'title': 'president', 'rank': 1}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['title'], 'President')


# --------------------------------------------------------------------------- create_profile_for_admin_user

class CreateProfileForAdminUserTests(TestCase):
    def test_creates_profile_with_defaults(self):
        user = make_user(email='newbie@example.com')
        profile = create_profile_for_admin_user(user, 'ram', 'shah')
        # Profile.save() proper-cases name fields, so 'ram' -> 'Ram'.
        self.assertEqual(profile.first_name, 'Ram')
        self.assertEqual(profile.last_name, 'Shah')
        self.assertEqual(profile.city, 'Jagatsinghpur')
        self.assertEqual(profile.pincode, '754134')

    def test_updates_existing_profile_names_only(self):
        user = make_user(email='existing@example.com')
        first = create_profile_for_admin_user(user, 'Old', 'Name')
        first.city = 'Cuttack'
        first.save(update_fields=['city'])

        updated = create_profile_for_admin_user(user, 'New', 'Name2')
        self.assertEqual(updated.pk, first.pk)
        self.assertEqual(updated.first_name, 'New')
        self.assertEqual(updated.last_name, 'Name2')
        # untouched field from the first call survives (only names are updated)
        self.assertEqual(updated.city, 'Cuttack')


# --------------------------------------------------------------------------- AdminAddProfileForm

class AdminAddProfileFormTests(TestCase):
    def test_names_are_proper_cased(self):
        form = AdminAddProfileForm(data={'first_name': 'ram', 'last_name': 'shah'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['first_name'], 'Ram')
        self.assertEqual(form.cleaned_data['last_name'], 'Shah')

    def test_blank_email_generates_placeholder_login(self):
        form = AdminAddProfileForm(data={'first_name': 'ram', 'last_name': 'shah', 'email': ''})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.cleaned_data['login_email'].endswith('@member.bandhu.local'))

    def test_new_unique_email_is_used_directly(self):
        form = AdminAddProfileForm(
            data={'first_name': 'ram', 'last_name': 'shah', 'email': 'Fresh@Example.com'}
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['login_email'], 'fresh@example.com')

    def test_admin_own_email_without_password_is_rejected(self):
        admin = make_admin(email='admin@example.com')
        form = AdminAddProfileForm(
            data={'first_name': 'ram', 'last_name': 'shah', 'email': 'admin@example.com'},
            admin_user=admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('admin_password', form.errors)

    def test_admin_own_email_with_correct_password_uses_placeholder(self):
        admin = make_admin(email='admin@example.com')
        form = AdminAddProfileForm(
            data={
                'first_name': 'ram',
                'last_name': 'shah',
                'email': 'admin@example.com',
                'admin_password': PASSWORD,
            },
            admin_user=admin,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.cleaned_data['login_email'].endswith('@member.bandhu.local'))

    def test_admin_own_email_with_wrong_password_is_rejected(self):
        admin = make_admin(email='admin@example.com')
        form = AdminAddProfileForm(
            data={
                'first_name': 'ram',
                'last_name': 'shah',
                'email': 'admin@example.com',
                'admin_password': 'totally-wrong',
            },
            admin_user=admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('admin_password', form.errors)
        self.assertIn('Incorrect admin password.', form.errors['admin_password'])

    def test_another_admins_email_is_rejected(self):
        make_admin(email='other-admin@example.com')
        acting_admin = make_admin(email='acting@example.com')
        form = AdminAddProfileForm(
            data={'first_name': 'ram', 'last_name': 'shah', 'email': 'other-admin@example.com'},
            admin_user=acting_admin,
        )
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn(
            'This email belongs to another admin account and cannot be reused.',
            form.errors['email'],
        )

    def test_taken_non_admin_email_is_rejected(self):
        make_user(email='taken@example.com')
        form = AdminAddProfileForm(
            data={'first_name': 'ram', 'last_name': 'shah', 'email': 'taken@example.com'}
        )
        self.assertFalse(form.is_valid())
        self.assertIn('A user with this email already exists.', form.errors['email'])

    def test_save_creates_user_and_profile_with_defaults(self):
        form = AdminAddProfileForm(data={'first_name': 'ram', 'last_name': 'shah', 'email': ''})
        self.assertTrue(form.is_valid(), form.errors)
        profile = form.save()
        self.assertEqual(profile.first_name, 'Ram')
        self.assertFalse(profile.user.is_admin)
        self.assertFalse(profile.user.is_staff)
        self.assertFalse(profile.user.has_usable_password())
        self.assertEqual(profile.city, 'Jagatsinghpur')


# --------------------------------------------------------------------------- RoleSelect widget

class RoleSelectTests(TestCase):
    def test_create_option_adds_designation_attr_for_known_role(self):
        widget = RoleSelect(role_designation_map={7: 3})
        option = widget.create_option('role', '7', 'President', False, 0)
        self.assertEqual(option['attrs']['data-designation-id'], '3')

    def test_create_option_skips_attr_for_unknown_role(self):
        widget = RoleSelect(role_designation_map={})
        option = widget.create_option('role', '99', 'Ghost', False, 0)
        self.assertNotIn('data-designation-id', option.get('attrs', {}))

    def test_create_option_skips_attr_for_blank_value(self):
        widget = RoleSelect(role_designation_map={7: 3})
        option = widget.create_option('role', '', '---------', False, 0)
        self.assertNotIn('data-designation-id', option.get('attrs', {}))

    def test_create_option_handles_non_numeric_value(self):
        widget = RoleSelect(role_designation_map={7: 3})
        option = widget.create_option('role', 'not-an-int', 'Odd', False, 0)
        self.assertNotIn('data-designation-id', option.get('attrs', {}))


# --------------------------------------------------------------------------- PeoplesDesignationAdminForm

class PeoplesDesignationAdminFormTests(TestCase):
    def setUp(self):
        self.office_bearers = Designation.objects.create(title='Office Bearers', rank=1)
        self.core_team = Designation.objects.create(title='Core Team', rank=2)
        self.role_a = DesignationRole.objects.create(
            designation=self.office_bearers, title='President', rank=1
        )
        self.other_designation = Designation.objects.create(title='Advisory', rank=3)
        self.role_b = DesignationRole.objects.create(
            designation=self.other_designation, title='Advisor', rank=1
        )
        user = make_user(email='staffer@example.com')
        profile = make_profile(user)
        self.staff = Staff.objects.create(profile=profile, about='Bio')

    def test_role_queryset_filtered_by_posted_designation(self):
        form = PeoplesDesignationAdminForm(
            data={
                'staff': self.staff.pk,
                'designation': self.office_bearers.pk,
                'role': self.role_a.pk,
                'desc': 'x',
                'rank': 1,
            }
        )
        role_qs = list(form.fields['role'].queryset)
        self.assertIn(self.role_a, role_qs)
        self.assertNotIn(self.role_b, role_qs)

    def test_role_queryset_filtered_by_instance_designation_when_unbound(self):
        existing = PeoplesDesignation.objects.create(
            staff=self.staff, designation=self.other_designation, role=self.role_b, rank=1
        )
        form = PeoplesDesignationAdminForm(instance=existing)
        role_qs = list(form.fields['role'].queryset)
        self.assertIn(self.role_b, role_qs)
        self.assertNotIn(self.role_a, role_qs)

    def test_clean_clears_role_for_core_team(self):
        form = PeoplesDesignationAdminForm(
            data={
                'staff': self.staff.pk,
                'designation': self.core_team.pk,
                'role': '',
                'desc': 'x',
                'rank': 1,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data['role'])

    def test_clean_rejects_role_from_other_designation(self):
        form = PeoplesDesignationAdminForm(
            data={
                'staff': self.staff.pk,
                'designation': self.office_bearers.pk,
                'role': self.role_a.pk,
                'desc': 'x',
                'rank': 1,
            }
        )
        # force a mismatched role into cleaned_data to hit the guard, since the
        # queryset filtering above would normally prevent this from validating.
        form.fields['role'].queryset = DesignationRole.objects.all()
        form.data = form.data.copy()
        form.data['role'] = self.role_b.pk
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)
        self.assertIn('belongs to a different designation', form.errors['role'][0])

    def test_clean_without_designation_returns_early(self):
        form = PeoplesDesignationAdminForm(
            data={'staff': self.staff.pk, 'designation': '', 'role': '', 'desc': '', 'rank': 1}
        )
        self.assertFalse(form.is_valid())
        # No extra 'role' error should be raised beyond the standard required-field error.
        self.assertNotIn('role', form.errors)


# --------------------------------------------------------------------------- PeoplesDesignationInlineFormSet

class PeoplesDesignationInlineFormSetTests(TestCase):
    def setUp(self):
        self.core_team = Designation.objects.create(title='Core Team', rank=1)
        self.office_bearers = Designation.objects.create(title='Office Bearers', rank=2)
        self.advisory = Designation.objects.create(title='Advisory', rank=3)
        self.role_president = DesignationRole.objects.create(
            designation=self.office_bearers, title='President', rank=1
        )
        self.role_secretary = DesignationRole.objects.create(
            designation=self.office_bearers, title='Secretary', rank=2
        )
        user = make_user(email='formset-staffer@example.com')
        profile = make_profile(user)
        self.staff = Staff.objects.create(profile=profile, about='Bio')
        self.FormSet = inlineformset_factory(
            Staff,
            PeoplesDesignation,
            form=PeoplesDesignationAdminForm,
            formset=PeoplesDesignationInlineFormSet,
            fields='__all__',
            extra=0,
            can_delete=True,
        )

    def _management_data(self, rows, prefix):
        data = {
            f'{prefix}-TOTAL_FORMS': str(len(rows)),
            f'{prefix}-INITIAL_FORMS': '0',
            f'{prefix}-MIN_NUM_FORMS': '0',
            f'{prefix}-MAX_NUM_FORMS': '1000',
        }
        for i, row in enumerate(rows):
            for key, value in row.items():
                data[f'{prefix}-{i}-{key}'] = value
        return data

    def _base_row(self, designation, role=''):
        return {
            'staff': self.staff.pk,
            'designation': designation.pk,
            'role': role,
            'desc': '',
            'rank': 1,
        }

    def _build(self, rows):
        prefix = self.FormSet(instance=self.staff).prefix
        data = self._management_data(rows, prefix)
        return self.FormSet(data, instance=self.staff, prefix=prefix)

    def test_rejects_two_core_team_rows(self):
        formset = self._build([
            self._base_row(self.core_team),
            self._base_row(self.core_team),
        ])
        self.assertFalse(formset.is_valid())
        self.assertIn('Only one Core Team row per person', formset.non_form_errors()[0])

    def test_office_bearers_row_requires_role(self):
        formset = self._build([self._base_row(self.office_bearers, role='')])
        self.assertFalse(formset.is_valid())
        # PeoplesDesignation.model.clean() rejects the missing role on the row
        # itself (a per-form field error), so the formset's own custom
        # "needs a position" non-form-error path never runs for this input.
        self.assertIn('role', formset.forms[0].errors)

    def test_duplicate_office_bearer_role_is_rejected(self):
        formset = self._build([
            self._base_row(self.office_bearers, role=self.role_president.pk),
            self._base_row(self.office_bearers, role=self.role_president.pk),
        ])
        self.assertFalse(formset.is_valid())
        # Both rows share (staff, designation, role), which is exactly the
        # model's unique_together, so Django's own cross-form uniqueness
        # check (BaseModelFormSet.validate_unique) raises first — with its
        # generic message — before PeoplesDesignationInlineFormSet.clean()'s
        # own "you added X twice" branch ever runs.
        self.assertIn('must be unique', formset.non_form_errors()[0])

    def test_duplicate_office_bearer_role_custom_message_when_reached(self):
        """The formset's own duplicate-role message (the ValidationError
        naming the role by title) is unreachable through the public
        is_valid()/save() path: Django's built-in unique_together check on
        (staff, designation, role) always intercepts first (see the test
        above). This exercises that branch directly, by bypassing Django's
        own uniqueness check, to confirm the custom detection logic itself
        is correct — even though production traffic never reaches it."""
        formset = self._build([
            self._base_row(self.office_bearers, role=self.role_president.pk),
            self._base_row(self.office_bearers, role=self.role_president.pk),
        ])
        from django.forms.models import BaseModelFormSet
        with mock.patch.object(BaseModelFormSet, 'validate_unique', lambda self: None):
            self.assertFalse(formset.is_valid())
        self.assertIn('twice', formset.non_form_errors()[0])

    def test_duplicate_generic_designation_row_is_rejected(self):
        formset = self._build([
            self._base_row(self.advisory),
            self._base_row(self.advisory),
        ])
        self.assertFalse(formset.is_valid())
        self.assertIn('Duplicate', formset.non_form_errors()[0])

    def test_valid_distinct_rows_pass(self):
        formset = self._build([
            self._base_row(self.core_team),
            self._base_row(self.office_bearers, role=self.role_president.pk),
            self._base_row(self.office_bearers, role=self.role_secretary.pk),
        ])
        self.assertTrue(formset.is_valid(), formset.errors)


# --------------------------------------------------------------------------- Staff experience forms

class StaffExperiencePhotoHelperTests(TempMediaMixin, TestCase):
    def setUp(self):
        user = make_user(email='experience-staffer@example.com')
        profile = make_profile(user)
        self.staff = Staff.objects.create(profile=profile, about='Bio')
        self.experience = StaffExperience.objects.create(staff=self.staff, message='Great work')

    def test_save_experience_photo_noop_without_image(self):
        _save_experience_photo(self.experience, None, 'caption')
        self.assertEqual(self.experience.photos.count(), 0)

    def test_save_experience_photo_creates_record(self):
        _save_experience_photo(self.experience, image_upload(), '  a caption  ')
        photo = self.experience.photos.get()
        self.assertEqual(photo.caption, 'a caption')

    def test_inline_form_save_attaches_photo(self):
        form = StaffExperienceInlineForm(
            data={'message': 'Nice'},
            files={'image': image_upload()},
            instance=self.experience,
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.photos.count(), 1)

    def test_inline_form_save_without_image_skips_photo(self):
        form = StaffExperienceInlineForm(data={'message': 'No photo'}, instance=self.experience)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(self.experience.photos.count(), 0)

    def test_standalone_admin_form_save_attaches_photo(self):
        form = StaffExperienceAdminForm(
            data={'staff': self.staff.pk, 'message': 'Standalone'},
            files={'image': image_upload()},
        )
        self.assertTrue(form.is_valid(), form.errors)
        instance = form.save()
        self.assertEqual(instance.photos.count(), 1)


# --------------------------------------------------------------------------- AnnualReportUploadForm

class AnnualReportUploadFormTests(TempMediaMixin, TestCase):
    def test_valid_with_pdf_only(self):
        form = AnnualReportUploadForm(
            data={'year': 2024, 'title': '', 'external_url': '', 'is_published': True},
            files={'pdf_file': file_upload()},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_with_url_only(self):
        form = AnnualReportUploadForm(
            data={
                'year': 2023,
                'title': '',
                'external_url': 'https://drive.google.com/file/d/abc',
                'is_published': True,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_without_pdf_or_url(self):
        form = AnnualReportUploadForm(
            data={'year': 2022, 'title': '', 'external_url': '', 'is_published': True}
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            'Upload a PDF file or paste a Google Drive / public link.',
            form.errors['__all__'][0],
        )

    def test_editing_existing_pdf_without_reupload_stays_valid(self):
        report = AnnualReport.objects.create(year=2021, pdf_file=file_upload())
        form = AnnualReportUploadForm(
            data={'year': 2021, 'title': '', 'external_url': '', 'is_published': True},
            instance=report,
        )
        self.assertTrue(form.is_valid(), form.errors)
