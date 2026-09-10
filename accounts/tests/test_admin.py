"""accounts admin wiring, admin helpers, tokens, context processor, User model."""

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from accounts.admin import UserAdmin
from accounts.admin_form_utils import admin_form_with_user
from accounts.admin_helpers import (
    apply_admin_created_user_defaults,
    build_placeholder_login_email,
    normalize_admin_add_email,
    resolve_admin_created_user_email,
)
from accounts.context_processors import login_modal, pop_login_modal_flash
from accounts.forms import AdminAddUserForm, UserAdminChangeForm
from accounts.models import User
from accounts.tokens import account_activation_token
from bandhuapp.tests.support import PASSWORD, make_admin, make_user


class UserAdminTests(TestCase):
    def setUp(self):
        self.admin = make_admin()
        self.client.force_login(self.admin)
        self.model_admin = admin.site._registry[User]

    def test_registered_with_custom_admin(self):
        self.assertIsInstance(self.model_admin, UserAdmin)
        self.assertEqual(admin.site.site_header, 'Bandhu')

    def test_changelist_lists_users_and_filters_by_admin_flag(self):
        make_user('member@example.com')
        response = self.client.get('/admin/accounts/user/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'member@example.com')
        response = self.client.get('/admin/accounts/user/?is_admin__exact=1')
        self.assertContains(response, self.admin.email)
        self.assertNotContains(response, 'member@example.com')
        response = self.client.get('/admin/accounts/user/?q=member')
        self.assertContains(response, 'member@example.com')

    def test_change_page_renders_and_updates_flags(self):
        member = make_user('member@example.com')
        url = '/admin/accounts/user/%d/change/' % member.pk
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        form = response.context['adminform'].form
        self.assertIsInstance(form, UserAdminChangeForm)
        response = self.client.post(url, {
            'email': member.email, 'password': member.password,
            'is_active': 'on', 'auth': 'on', '_save': 'Save',
        })
        self.assertRedirects(response, '/admin/accounts/user/', fetch_redirect_response=False)
        member.refresh_from_db()
        self.assertTrue(member.auth)
        self.assertFalse(member.is_admin)
        self.assertTrue(member.check_password(PASSWORD))

    def test_admin_password_change_view(self):
        member = make_user('member@example.com')
        url = '/admin/accounts/user/%d/password/' % member.pk
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {'password1': 'N3w-pass-word!', 'password2': 'N3w-pass-word!'})
        self.assertEqual(response.status_code, 302)
        member.refresh_from_db()
        self.assertTrue(member.check_password('N3w-pass-word!'))

    def test_get_form_for_existing_user_is_change_form(self):
        request = RequestFactory().get('/admin/accounts/user/')
        request.user = self.admin
        form_class = self.model_admin.get_form(request, obj=self.admin)
        self.assertTrue(issubclass(form_class, UserAdminChangeForm))

    def test_get_form_for_add_binds_admin_user(self):
        request = RequestFactory().get('/admin/accounts/user/add/')
        request.user = self.admin
        form_class = self.model_admin.get_form(request)
        self.assertTrue(issubclass(form_class, AdminAddUserForm))
        form = form_class({'first_name': 'a', 'last_name': 'b', 'email': self.admin.email, 'admin_password': PASSWORD})
        self.assertIs(form.admin_user, self.admin)
        self.assertTrue(form.is_valid(), form.errors)


class AdminFormWithUserTests(TestCase):
    def test_wrapper_keeps_name_and_injects_admin_user(self):
        admin_user = make_admin()
        wrapped = admin_form_with_user(AdminAddUserForm, admin_user)
        self.assertEqual(wrapped.__name__, 'AdminAddUserForm')
        self.assertEqual(wrapped.__module__, AdminAddUserForm.__module__)
        self.assertIs(wrapped().admin_user, admin_user)
        self.assertIsNone(AdminAddUserForm().admin_user)


class AdminHelpersTests(TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_admin_add_email('  Foo@Bar.COM '), 'foo@bar.com')
        self.assertEqual(normalize_admin_add_email(None), '')
        self.assertEqual(normalize_admin_add_email(''), '')

    def test_placeholder_slug(self):
        email = build_placeholder_login_email('Ravi', "O'Neil Jr.")
        self.assertRegex(email, r"^ravi-o-neil-jr\.[0-9a-f]{10}@member\.bandhu\.local$")

    def test_placeholder_falls_back_to_member_and_truncates(self):
        self.assertRegex(build_placeholder_login_email('', ''), r'^member\.[0-9a-f]{10}@member\.bandhu\.local$')
        self.assertRegex(build_placeholder_login_email('!!!', '###'), r'^member\.')
        slug = build_placeholder_login_email('a' * 60, 'b').split('.')[0]
        self.assertEqual(len(slug), 40)

    def test_placeholders_are_unique(self):
        self.assertNotEqual(build_placeholder_login_email('a', 'b'), build_placeholder_login_email('a', 'b'))

    def resolve(self, email, admin_user=None, password=''):
        return resolve_admin_created_user_email(
            entered_email=email, admin_user=admin_user, admin_password=password,
            first_name='Ravi', last_name='Kumar',
        )

    def test_blank_email_gives_placeholder(self):
        self.assertTrue(self.resolve('   ').startswith('ravi-kumar.'))

    def test_unused_email_is_returned_normalised(self):
        self.assertEqual(self.resolve(' New@Example.com '), 'new@example.com')

    def test_existing_member_email_is_rejected(self):
        make_user('member@example.com')
        with self.assertRaises(ValidationError) as ctx:
            self.resolve('MEMBER@example.com')
        self.assertEqual(ctx.exception.messages, ['A user with this email already exists.'])
        self.assertIsNone(ctx.exception.code)

    def test_other_admin_email_is_rejected(self):
        admin_user = make_admin()
        make_admin('other@example.com')
        with self.assertRaises(ValidationError) as ctx:
            self.resolve('other@example.com', admin_user=admin_user, password=PASSWORD)
        self.assertIn('another admin account', ctx.exception.messages[0])

    def test_staff_only_email_counts_as_admin_email(self):
        make_user('staff@example.com', is_staff=True)
        with self.assertRaises(ValidationError) as ctx:
            self.resolve('staff@example.com', admin_user=None)
        self.assertIn('another admin account', ctx.exception.messages[0])

    def test_own_email_requires_password(self):
        admin_user = make_admin()
        with self.assertRaises(ValidationError) as ctx:
            self.resolve(admin_user.email, admin_user=admin_user)
        self.assertEqual(ctx.exception.code, 'admin_password_required')

    def test_own_email_with_wrong_password(self):
        admin_user = make_admin()
        with self.assertRaises(ValidationError) as ctx:
            self.resolve(admin_user.email, admin_user=admin_user, password='wrong')
        self.assertEqual(ctx.exception.code, 'admin_password_invalid')

    def test_own_email_with_correct_password_gives_placeholder(self):
        admin_user = make_admin()
        login = self.resolve(admin_user.email, admin_user=admin_user, password=PASSWORD)
        self.assertTrue(login.startswith('ravi-kumar.'))
        self.assertTrue(login.endswith('@member.bandhu.local'))

    def test_defaults_make_regular_member_without_password(self):
        user = User(email='x@example.com', is_admin=True, is_staff=True, is_active=False)
        apply_admin_created_user_defaults(user)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.auth)
        self.assertFalse(user.has_usable_password())


class TokenTests(TestCase):
    def test_token_invalidates_when_active_or_auth_flags_change(self):
        user = make_user(is_active=False, auth=False)
        token = account_activation_token.make_token(user)
        self.assertTrue(account_activation_token.check_token(user, token))
        user.is_active = True
        self.assertFalse(account_activation_token.check_token(user, token))
        user.is_active = False
        user.auth = True
        self.assertFalse(account_activation_token.check_token(user, token))
        self.assertFalse(account_activation_token.check_token(user, 'garbage'))
        self.assertFalse(account_activation_token.check_token(make_user('other@example.com', is_active=False), token))


class LoginModalContextProcessorTests(TestCase):
    def request(self, path='/', session=None):
        request = RequestFactory().get(path)
        request.session = session if session is not None else {}
        return request

    def test_pop_flash_with_no_state(self):
        request = self.request()
        self.assertEqual(pop_login_modal_flash(request), {'login_modal_err_code': 0, 'login_modal_prefill_email': ''})

    def test_pop_flash_consumes_session_values(self):
        request = self.request(session={'login_modal_err_code': '3', 'login_modal_prefill_email': 'a@b.c'})
        self.assertEqual(pop_login_modal_flash(request), {'login_modal_err_code': 3, 'login_modal_prefill_email': 'a@b.c'})
        self.assertEqual(request.session, {})

    def test_pop_flash_ignores_non_numeric_code_and_null_prefill(self):
        request = self.request(session={'login_modal_err_code': 'bogus', 'login_modal_prefill_email': None})
        self.assertEqual(pop_login_modal_flash(request), {'login_modal_err_code': 0, 'login_modal_prefill_email': ''})

    def test_login_modal_opens_from_query_and_pops_flash(self):
        request = self.request('/?login_modal=1', session={'login_modal_err_code': 2})
        context = login_modal(request)
        self.assertEqual(context, {'login_modal_err_code': 2, 'login_modal_prefill_email': '', 'open_login_modal': True})
        self.assertFalse(login_modal(self.request())['open_login_modal'])

    def test_login_modal_skips_flash_when_already_consumed(self):
        request = self.request('/?login_modal=1', session={'login_modal_err_code': 2, 'login_modal_prefill_email': 'x'})
        request._login_modal_flash_consumed = True
        context = login_modal(request)
        self.assertEqual(context, {'login_modal_err_code': 0, 'open_login_modal': True, 'login_modal_prefill_email': ''})
        self.assertEqual(request.session['login_modal_err_code'], 2)

    def test_context_processor_runs_on_real_page(self):
        session = self.client.session
        session['login_modal_err_code'] = 3
        session['login_modal_prefill_email'] = 'who@example.com'
        session.save()
        response = self.client.get('/accounts/password_reset/?login_modal=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['login_modal_err_code'], 3)
        self.assertEqual(response.context['login_modal_prefill_email'], 'who@example.com')
        self.assertTrue(response.context['open_login_modal'])
        self.assertNotIn('login_modal_err_code', self.client.session)


class UserModelTests(TestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user('', 'pw')

    def test_create_user_normalises_domain(self):
        user = User.objects.create_user('Person@EXAMPLE.com', 'pw')
        self.assertEqual(user.email, 'Person@example.com')
        self.assertTrue(user.check_password('pw'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_admin)

    def test_create_staffuser_and_superuser(self):
        staff = User.objects.create_staffuser('staff@example.com', 'pw')
        self.assertTrue(staff.is_staff)
        self.assertFalse(staff.is_admin)
        boss = User.objects.create_superuser('boss@example.com', 'pw')
        self.assertTrue(boss.is_staff)
        self.assertTrue(boss.is_admin)

    def test_identity_and_permission_helpers(self):
        user = make_user(is_staff=True, is_admin=True, is_active=False)
        self.assertEqual(str(user), user.email)
        self.assertEqual(user.get_full_name(), user.email)
        self.assertEqual(user.get_short_name(), user.email)
        self.assertTrue(user.has_perm('anything'))
        self.assertTrue(user.has_module_perms('bandhuapp'))
        self.assertTrue(user.if_staff)
        self.assertTrue(user.if_admin)
        self.assertFalse(user.if_active)
        self.assertIsNotNone(user.signup_time)
