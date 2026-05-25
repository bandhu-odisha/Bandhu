"""
Create a dummy admin user for login.
Run: python manage.py create_admin_user
"""
from datetime import date

from django.core.management.base import BaseCommand

from accounts.models import User
from bandhuapp.models import Profile, Staff


class Command(BaseCommand):
    help = 'Creates a dummy admin user (admin@bandhu.demo / admin123) if not present.'

    def handle(self, *args, **options):
        email = 'admin@bandhu.demo'
        password = 'admin123'

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'is_admin': True,
                'is_staff': True,
                'is_active': True,
                'auth': True,
            },
        )
        if created:
            user.set_password(password)
            user.is_admin = True
            user.is_staff = True
            user.is_active = True
            user.auth = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {email} / {password}'))
        else:
            self.stdout.write(self.style.WARNING(f'User {email} already exists. Password unchanged.'))
            # Ensure permission flags (idempotent)
            dirty = False
            if not user.is_admin:
                user.is_admin = True
                dirty = True
            if not user.is_staff:
                user.is_staff = True
                dirty = True
            if not user.is_active:
                user.is_active = True
                dirty = True
            if not user.auth:
                user.auth = True
                dirty = True
            if dirty:
                user.save()

        # Home / landing require a Profile for regular members; create a minimal one for admin.
        profile, p_created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'first_name': 'Site',
                'last_name': 'Administrator',
                'gender': 'M',
                'dob': date(1990, 1, 1),
                'contact_no': '0000000000',
                'street_address1': 'Bandhu',
                'street_address2': '',
                'city': 'Jagatsinghpur',
                'state': 'Odisha',
                'pincode': '754134',
                'profession': 'Administrator',
            },
        )
        if p_created:
            self.stdout.write(self.style.SUCCESS('Linked a minimal Profile for admin (edit under /profile/ if needed).'))
        else:
            self.stdout.write('Profile already present for admin user.')

        staff, s_created = Staff.objects.get_or_create(
            profile=profile,
            defaults={'about': 'Site administrator.'},
        )
        if s_created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Created Staff record — add designations under Django admin → Staff.'
                )
            )
        else:
            self.stdout.write('Staff record already present for admin user.')

        self.stdout.write('Login at: /accounts/login/')
