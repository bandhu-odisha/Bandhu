"""accounts/forms.py: register, admin add/change, password-reset mail."""

from unittest import mock

from django.test import TestCase

from accounts.forms import (
    AdminAddUserForm,
    CustomPasswordResetForm,
    RegisterForm,
    UserAdminChangeForm,
    UserAdminCreationForm,
)
from accounts.models import User
from bandhuapp.models import Profile
from bandhuapp.tests.support import PASSWORD, make_admin, make_user


class RegisterFormTests(TestCase):
    def test_valid_data(self):
        form = RegisterForm({'email': 'new@example.com', 'password': PASSWORD, 'password2': PASSWORD})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'new@example.com')

    def test_taken_email(self):
        make_user('taken@example.com')
        form = RegisterForm({'email': 'taken@example.com', 'password': PASSWORD, 'password2': PASSWORD})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['Email is taken'])

    def test_password_mismatch(self):
        form = RegisterForm({'email': 'new@example.com', 'password': PASSWORD, 'password2': 'other'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ["Passwords don't match"])

    def test_missing_password2_does_not_trigger_mismatch(self):
        form = RegisterForm({'email': 'new@example.com', 'password': PASSWORD, 'password2': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['This field is required.'])


class UserAdminCreationFormTests(TestCase):
    def test_save_sets_password(self):
        form = UserAdminCreationForm({'email': 'legacy@example.com', 'password1': PASSWORD, 'password2': PASSWORD})
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertIsNotNone(user.pk)
        self.assertTrue(User.objects.get(email='legacy@example.com').check_password(PASSWORD))

    def test_save_without_commit_does_not_persist(self):
        form = UserAdminCreationForm({'email': 'legacy@example.com', 'password1': PASSWORD, 'password2': PASSWORD})
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=False)
        self.assertIsNone(user.pk)
        self.assertTrue(user.check_password(PASSWORD))
        self.assertFalse(User.objects.filter(email='legacy@example.com').exists())

    def test_password_mismatch(self):
        form = UserAdminCreationForm({'email': 'legacy@example.com', 'password1': PASSWORD, 'password2': 'nope'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ["Passwords don't match"])


class AdminAddUserFormTests(TestCase):
    def setUp(self):
        self.admin = make_admin()

    def form(self, **data):
        payload = {'first_name': 'ravi', 'last_name': 'kUMAR', 'email': '', 'admin_password': ''}
        payload.update(data)
        return AdminAddUserForm(payload, admin_user=self.admin)

    def test_blank_email_generates_placeholder_login(self):
        form = self.form()
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['first_name'], 'Ravi')
        self.assertEqual(form.cleaned_data['last_name'], 'Kumar')
        login = form.cleaned_data['login_email']
        self.assertTrue(login.startswith('ravi-kumar.'))
        self.assertTrue(login.endswith('@member.bandhu.local'))

    def test_new_email_is_normalised_and_used(self):
        form = self.form(email='  New.Member@Example.com ')
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['email'], 'new.member@example.com')
        self.assertEqual(form.cleaned_data['login_email'], 'new.member@example.com')

    def test_taken_member_email_is_rejected(self):
        make_user('member@example.com')
        form = self.form(email='member@example.com')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['email'], ['A user with this email already exists.'])
        self.assertNotIn('login_email', form.cleaned_data)

    def test_other_admin_email_is_rejected(self):
        make_admin('other-admin@example.com')
        form = self.form(email='other-admin@example.com')
        self.assertFalse(form.is_valid())
        self.assertIn('another admin account', form.errors['email'][0])

    def test_own_admin_email_requires_password(self):
        form = self.form(email=self.admin.email)
        self.assertFalse(form.is_valid())
        self.assertNotIn('email', form.errors)
        self.assertIn('Enter your admin password', form.errors['admin_password'][0])

    def test_own_admin_email_with_wrong_password(self):
        form = self.form(email=self.admin.email, admin_password='wrong')
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['admin_password'], ['Incorrect admin password.'])

    def test_own_admin_email_with_correct_password_gets_placeholder(self):
        form = self.form(email=self.admin.email, admin_password=PASSWORD)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertNotEqual(form.cleaned_data['login_email'], self.admin.email)
        self.assertTrue(form.cleaned_data['login_email'].endswith('@member.bandhu.local'))

    def test_field_errors_skip_email_resolution(self):
        form = self.form(first_name='', email='bad-email')
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertNotIn('admin_password', form.errors)

    def test_save_creates_member_and_profile(self):
        form = self.form(email='fresh@example.com')
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        user.refresh_from_db()
        self.assertEqual(user.email, 'fresh@example.com')
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.auth)
        self.assertFalse(user.has_usable_password())
        profile = Profile.objects.get(user=user)
        self.assertEqual((profile.first_name, profile.last_name), ('Ravi', 'Kumar'))

    def test_save_without_commit(self):
        form = self.form(email='fresh@example.com')
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save(commit=False)
        self.assertIsNone(user.pk)
        self.assertFalse(User.objects.filter(email='fresh@example.com').exists())
        self.assertEqual(Profile.objects.count(), 0)


class UserAdminChangeFormTests(TestCase):
    def test_password_field_keeps_initial_hash(self):
        user = make_user()
        original_hash = user.password
        form = UserAdminChangeForm(
            {'email': user.email, 'password': 'tampered', 'is_active': 'on', 'is_admin': 'on', 'auth': 'on'},
            instance=user,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['password'], original_hash)
        saved = form.save()
        saved.refresh_from_db()
        self.assertEqual(saved.password, original_hash)
        self.assertTrue(saved.is_admin)
        self.assertFalse(saved.is_staff)


@mock.patch('accounts.forms.SendGridAPIClient')
class CustomPasswordResetFormSendMailTests(TestCase):
    SUBJECT = 'registration/password_reset_subject.txt'
    BODY = 'registration/password_reset_email.html'

    def setUp(self):
        self.user = make_user('reset@example.com')
        self.context = {
            'email': self.user.email, 'domain': 'testserver', 'site_name': 'Bandhu',
            'uid': 'uid', 'user': self.user, 'token': 'token', 'protocol': 'http',
        }

    def sent_mail(self, sendgrid):
        sendgrid.return_value.send.assert_called_once()
        return sendgrid.return_value.send.call_args[0][0].get()

    def test_plain_template_is_sent_as_html_content(self, sendgrid):
        CustomPasswordResetForm().send_mail(
            self.SUBJECT, self.BODY, self.context, 'noreply@example.com', 'reset@example.com',
        )
        message = self.sent_mail(sendgrid)
        self.assertEqual(message['from']['email'], 'noreply@example.com')
        self.assertEqual(message['personalizations'][0]['to'][0]['email'], 'reset@example.com')
        self.assertNotIn('\n', message['subject'])
        self.assertEqual(message['content'][0]['type'], 'text/html')
        self.assertIn('token', message['content'][0]['value'])

    def test_html_template_overrides_body(self, sendgrid):
        with mock.patch('accounts.forms.loader.render_to_string', side_effect=['Subj\nect', 'plain', '<b>html</b>']) as render:
            CustomPasswordResetForm().send_mail(
                self.SUBJECT, self.BODY, self.context, 'noreply@example.com', 'reset@example.com',
                html_email_template_name='custom.html',
            )
        self.assertEqual(render.call_args_list[2][0][0], 'custom.html')
        message = self.sent_mail(sendgrid)
        self.assertEqual(message['subject'], 'Subject')
        self.assertEqual(message['content'][0]['value'], '<b>html</b>')

    def test_sendgrid_error_is_swallowed(self, sendgrid):
        sendgrid.return_value.send.side_effect = RuntimeError('down')
        with self.assertLogs('accounts.forms', level='ERROR') as logs:
            CustomPasswordResetForm().send_mail(
                self.SUBJECT, self.BODY, self.context, 'noreply@example.com', 'reset@example.com',
            )
        self.assertIn('SendGrid send failed', logs.output[0])
        self.assertIn('RuntimeError: down', logs.output[0])
