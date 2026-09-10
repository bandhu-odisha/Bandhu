"""Login, signup, activation, admin verification, password reset."""

from unittest import mock

from django.core import mail
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.models import User
from accounts.tokens import account_activation_token
from accounts.views import _is_safe_login_modal_next, _is_safe_signup_modal_next
from bandhuapp.tests.support import PASSWORD, make_profile, make_user

LOGIN = '/accounts/login/'
SIGNUP = '/accounts/signup/'


def uid_for(user):
    return urlsafe_base64_encode(force_bytes(user.pk))


class LoginViewTests(TestCase):
    def test_get_renders_form(self):
        response = self.client.get(LOGIN)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_code'], 0)

    def test_member_with_profile_logs_in_and_lands_home(self):
        user = make_user(auth=True)
        make_profile(user)
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD})
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_member_without_profile_is_sent_to_profile_page(self):
        user = make_user()
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD})
        self.assertRedirects(response, '/profile/', fetch_redirect_response=False)

    def test_safe_next_is_honoured(self):
        user = make_user(auth=True)
        make_profile(user)
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD, 'next': '/people/'})
        self.assertRedirects(response, '/people/', fetch_redirect_response=False)

    def test_external_next_is_ignored(self):
        user = make_user(auth=True)
        make_profile(user)
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD, 'next': 'https://evil.example/'})
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_wrong_password_reports_err_code_3(self):
        user = make_user()
        response = self.client.post(LOGIN, {'email': user.email, 'password': 'nope'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['err_code'], 3)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_unknown_email_reports_err_code_3(self):
        response = self.client.post(LOGIN, {'email': 'nobody@example.com', 'password': 'x'})
        self.assertEqual(response.context['err_code'], 3)

    def test_inactive_account_reports_err_code_1(self):
        user = make_user(is_active=False)
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD})
        self.assertEqual(response.context['err_code'], 1)

    def test_unverified_member_with_profile_reports_err_code_2(self):
        user = make_user(auth=False)
        make_profile(user)
        response = self.client.post(LOGIN, {'email': user.email, 'password': PASSWORD})
        self.assertEqual(response.context['err_code'], 2)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_modal_failure_redirects_back_with_flash(self):
        response = self.client.post(LOGIN, {
            'email': 'nobody@example.com', 'password': 'x', 'login_modal': '1', 'next': '/people/',
        })
        self.assertRedirects(response, '/people/?login_modal=1', fetch_redirect_response=False)
        self.assertEqual(self.client.session['login_modal_err_code'], 3)
        self.assertEqual(self.client.session['login_modal_prefill_email'], 'nobody@example.com')

    def test_login_modal_failure_keeps_existing_query_string(self):
        response = self.client.post(LOGIN, {
            'email': 'nobody@example.com', 'password': 'x', 'login_modal': '1', 'next': '/people/?tab=all',
        })
        self.assertRedirects(response, '/people/?tab=all&login_modal=1', fetch_redirect_response=False)

    def test_login_modal_failure_on_home_goes_to_react_home(self):
        response = self.client.post(LOGIN, {'email': 'nobody@example.com', 'password': 'x', 'login_modal': '1'})
        self.assertRedirects(response, '/?login_modal=1&next=%2F', fetch_redirect_response=False)

    def test_authenticated_user_is_redirected_home(self):
        self.client.force_login(make_user())
        self.assertRedirects(self.client.get(LOGIN), '/', fetch_redirect_response=False)

    def test_logout_returns_home(self):
        self.client.force_login(make_user())
        response = self.client.get('/accounts/logout/')
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertNotIn('_auth_user_id', self.client.session)


class SafeNextHelperTests(TestCase):
    def test_login_modal_next(self):
        self.assertTrue(_is_safe_login_modal_next('/people/'))
        self.assertFalse(_is_safe_login_modal_next('//evil.example'))
        self.assertFalse(_is_safe_login_modal_next('https://evil.example'))
        self.assertFalse(_is_safe_login_modal_next('/accounts/login/'))
        self.assertFalse(_is_safe_login_modal_next(''))
        self.assertFalse(_is_safe_login_modal_next(None))

    def test_signup_modal_next_only_allows_detail_pages(self):
        self.assertTrue(_is_safe_signup_modal_next('/anandakendra/detail/x/'))
        self.assertTrue(_is_safe_signup_modal_next('/ankurayan/detail/x/'))
        self.assertFalse(_is_safe_signup_modal_next('/people/'))
        self.assertFalse(_is_safe_signup_modal_next('//evil.example'))
        self.assertFalse(_is_safe_signup_modal_next(None))


@mock.patch('accounts.views.SendGridAPIClient')
class SignupViewTests(TestCase):
    def test_get_renders_form(self, _sendgrid):
        response = self.client.get(SIGNUP)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_valid_signup_creates_inactive_user_and_emails_activation(self, sendgrid):
        response = self.client.post(SIGNUP, {
            'email': 'new@example.com', 'password': PASSWORD, 'password2': PASSWORD,
        })
        self.assertRedirects(response, '/accounts/signup/success/', fetch_redirect_response=False)
        user = User.objects.get(email='new@example.com')
        self.assertFalse(user.is_active)
        self.assertFalse(user.auth)
        self.assertTrue(user.check_password(PASSWORD))
        sendgrid.return_value.send.assert_called_once()
        sent = sendgrid.return_value.send.call_args[0][0]
        self.assertIn(account_activation_token.make_token(user), sent.get()['content'][0]['value'])

    def test_sendgrid_failure_does_not_break_signup(self, sendgrid):
        sendgrid.return_value.send.side_effect = RuntimeError('sendgrid down')
        with self.assertLogs('accounts.views', level='ERROR'):
            response = self.client.post(SIGNUP, {
                'email': 'new@example.com', 'password': PASSWORD, 'password2': PASSWORD,
            })
        self.assertRedirects(response, '/accounts/signup/success/', fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_duplicate_email_is_rejected(self, _sendgrid):
        make_user('taken@example.com')
        response = self.client.post(SIGNUP, {
            'email': 'taken@example.com', 'password': PASSWORD, 'password2': PASSWORD,
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('already been taken', response.context['message'])
        self.assertEqual(User.objects.filter(email='taken@example.com').count(), 1)

    def test_duplicate_email_from_modal_redirects_back(self, _sendgrid):
        make_user('taken@example.com')
        response = self.client.post(SIGNUP, {
            'email': 'taken@example.com', 'password': PASSWORD, 'password2': PASSWORD,
            'signup_modal': '1', 'next': '/ankurayan/detail/fest/',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/ankurayan/detail/fest/'))

    def test_password_mismatch_is_rejected(self, _sendgrid):
        response = self.client.post(SIGNUP, {
            'email': 'new@example.com', 'password': PASSWORD, 'password2': 'different',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('password2', response.context['form'].errors)
        self.assertFalse(User.objects.filter(email='new@example.com').exists())

    def test_signup_modal_errors_redirect_back_to_detail_page(self, _sendgrid):
        response = self.client.post(SIGNUP, {
            'email': 'bad', 'password': PASSWORD, 'password2': 'x',
            'signup_modal': '1', 'next': '/anandakendra/detail/some-kendra/',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith('/anandakendra/detail/some-kendra/'))
        self.assertEqual(self.client.session['signup_modal_prefill_email'], 'bad')

    def test_signup_modal_with_unsafe_next_falls_back_to_full_page(self, _sendgrid):
        response = self.client.post(SIGNUP, {
            'email': 'bad', 'password': PASSWORD, 'password2': 'x',
            'signup_modal': '1', 'next': 'https://evil.example/',
        })
        self.assertEqual(response.status_code, 200)


class ActivationAndVerificationTests(TestCase):
    def test_valid_activation_link_activates_and_logs_in(self):
        user = make_user(is_active=False)
        token = account_activation_token.make_token(user)
        response = self.client.get(f'/accounts/activate/{uid_for(user)}/{token}/')
        self.assertRedirects(response, '/profile/', fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_activation_link_is_single_use(self):
        user = make_user(is_active=False)
        token = account_activation_token.make_token(user)
        url = f'/accounts/activate/{uid_for(user)}/{token}/'
        self.client.get(url)
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'token_expired.html')

    def test_bad_activation_link_renders_expired_page(self):
        response = self.client.get('/accounts/activate/xyz/bad-token/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'token_expired.html')

    @mock.patch('accounts.views.SendGridAPIClient')
    def test_admin_verification_link_sets_auth_flag(self, sendgrid):
        user = make_user(auth=False)
        token = account_activation_token.make_token(user)
        response = self.client.get(f'/accounts/authenticate/{uid_for(user)}/{token}/')
        self.assertRedirects(response, '/accounts/authenticated/', fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.auth)
        sendgrid.return_value.send.assert_called_once()

    @mock.patch('accounts.views.SendGridAPIClient')
    def test_verification_survives_sendgrid_failure_and_bad_token(self, sendgrid):
        sendgrid.return_value.send.side_effect = RuntimeError('down')
        user = make_user(auth=False)
        token = account_activation_token.make_token(user)
        with self.assertLogs('accounts.views', level='ERROR'):
            self.client.get(f'/accounts/authenticate/{uid_for(user)}/{token}/')
        user.refresh_from_db()
        self.assertTrue(user.auth)
        response = self.client.get('/accounts/authenticate/xyz/bad-token/')
        self.assertTemplateUsed(response, 'token_expired.html')

    def test_deletion_link_shows_confirmation_then_deletes(self):
        user = make_user()
        make_profile(user)
        token = account_activation_token.make_token(user)
        uid = uid_for(user)
        response = self.client.get(f'/accounts/delete/{uid}/{token}/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account_deletion_confirmation.html')
        with mock.patch('accounts.views.SendGridAPIClient') as sendgrid:
            sendgrid.return_value.send.side_effect = RuntimeError('down')
            with self.assertLogs('accounts.views', level='ERROR'):
                response = self.client.get(f'/accounts/delete_confirmed/{uid}/')
        self.assertRedirects(response, '/accounts/deleted/', fetch_redirect_response=False)
        self.assertFalse(User.objects.filter(pk=user.pk).exists())

    def test_deletion_bad_links(self):
        response = self.client.get('/accounts/delete/xyz/bad-token/')
        self.assertTemplateUsed(response, 'token_expired.html')
        self.assertEqual(self.client.get('/accounts/delete_confirmed/xyz/').status_code, 404)


class PasswordResetTests(TestCase):
    def test_form_renders(self):
        self.assertEqual(self.client.get('/accounts/password_reset/').status_code, 200)

    @mock.patch('accounts.forms.SendGridAPIClient')
    def test_reset_request_sends_via_sendgrid_and_redirects(self, sendgrid):
        make_user('reset@example.com')
        response = self.client.post('/accounts/password_reset/', {'email': 'reset@example.com'})
        self.assertRedirects(response, '/accounts/password_reset/done/', fetch_redirect_response=False)
        sendgrid.return_value.send.assert_called_once()
        self.assertEqual(len(mail.outbox), 0)

    @mock.patch('accounts.forms.SendGridAPIClient')
    def test_reset_request_survives_sendgrid_failure(self, sendgrid):
        sendgrid.return_value.send.side_effect = RuntimeError('down')
        make_user('reset@example.com')
        with self.assertLogs('accounts.forms', level='ERROR'):
            response = self.client.post('/accounts/password_reset/', {'email': 'reset@example.com'})
        self.assertRedirects(response, '/accounts/password_reset/done/', fetch_redirect_response=False)

    def test_reset_confirm_bad_token_renders(self):
        response = self.client.get('/accounts/reset/xyz/bad-token/')
        self.assertEqual(response.status_code, 200)

    def test_password_change_for_logged_in_user(self):
        user = make_user()
        self.client.force_login(user)
        self.assertEqual(self.client.get('/accounts/password_change/').status_code, 200)
        response = self.client.post('/accounts/password_change/', {
            'old_password': PASSWORD, 'new_password1': 'N3w-pass-word!', 'new_password2': 'N3w-pass-word!',
        })
        self.assertRedirects(response, '/accounts/password_change/done/', fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password('N3w-pass-word!'))
