import io

from django.core.management import call_command
from django.test import TestCase

from accounts.models import User
from bandhuapp.models import Profile, Staff
from bandhuapp.tests.support import TempMediaMixin


def run(*args):
    out = io.StringIO()
    call_command('create_admin_user', *args, stdout=out)
    return out.getvalue()


class CreateAdminUserCommandTests(TempMediaMixin, TestCase):
    def test_creates_demo_admin_with_profile_and_staff(self):
        output = run()
        user = User.objects.get(email='admin@bandhu.demo')
        self.assertTrue(user.check_password('admin123'))
        for flag in ('is_admin', 'is_staff', 'is_active', 'auth', 'is_superuser'):
            self.assertTrue(getattr(user, flag), flag)
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)
        self.assertEqual(Staff.objects.filter(profile__user=user).count(), 1)
        self.assertIn('Admin user created', output)

    def test_rerun_keeps_existing_password(self):
        run()
        user = User.objects.get(email='admin@bandhu.demo')
        user.set_password('changed')
        user.save()
        output = run()
        user.refresh_from_db()
        self.assertTrue(user.check_password('changed'))
        self.assertIn('already exists', output)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Staff.objects.count(), 1)

    def test_reset_password_flag(self):
        run()
        user = User.objects.get(email='admin@bandhu.demo')
        user.set_password('changed')
        user.save()
        output = run('--reset-password')
        user.refresh_from_db()
        self.assertTrue(user.check_password('admin123'))
        self.assertIn('Password reset', output)

    def test_demo_admin_can_log_in_and_use_django_admin(self):
        run()
        self.assertTrue(self.client.login(email='admin@bandhu.demo', password='admin123'))
        self.assertEqual(self.client.get('/admin/').status_code, 200)
        self.assertEqual(self.client.get('/').status_code, 200)
