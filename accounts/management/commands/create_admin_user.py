"""
Create a dummy admin user for login.
Run: python manage.py create_admin_user
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a dummy admin user (admin@bandhu.demo / admin123) if not present.'

    def handle(self, *args, **options):
        email = 'admin@bandhu.demo'
        password = 'admin123'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'User {email} already exists. Password unchanged.'))
            self.stdout.write('To reset password, use: python manage.py shell')
            return

        user = User.objects.create_user(email=email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.auth = True  # so login works without "admin authentication" step
        user.save(update_fields=['is_admin', 'is_staff', 'is_active', 'auth'])

        self.stdout.write(self.style.SUCCESS(f'Admin user created: {email} / {password}'))
        self.stdout.write('Login at: /accounts/login/')
