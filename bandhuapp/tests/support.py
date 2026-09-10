"""Shared helpers for the regression suite (users, profiles, uploads, temp media)."""

import shutil
import tempfile
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from accounts.models import User
from bandhuapp.models import Profile

# Smallest valid GIF (1x1). Enough for ImageField uploads without Pillow validation.
TINY_GIF = (
    b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04'
    b'\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
)
PASSWORD = 'Str0ng-pass-123'


def make_user(email='member@example.com', password=PASSWORD, **fields):
    user = User(email=email, **fields)
    user.set_password(password)
    user.save()
    return user


def make_admin(email='admin@example.com', password=PASSWORD):
    """Site admin: `is_admin` drives on-page controls, `is_staff` unlocks /admin/."""
    return make_user(email, password, is_admin=True, is_staff=True, auth=True)


def make_profile(user, **overrides):
    data = dict(
        first_name='Test',
        last_name='Member',
        gender='M',
        dob=date(1990, 1, 1),
        contact_no='9999999999',
        street_address1='1 Main Street',
        city='Cuttack',
        state='Odisha',
        pincode='753001',
        profession='Volunteer',
    )
    data.update(overrides)
    return Profile.objects.create(user=user, **data)


def image_upload(name='photo.gif'):
    return SimpleUploadedFile(name, TINY_GIF, content_type='image/gif')


def file_upload(name='report.pdf', content=b'%PDF-1.4 test'):
    return SimpleUploadedFile(name, content, content_type='application/pdf')


class TempMediaMixin:
    """Point MEDIA_ROOT at a throwaway directory for the whole test class."""

    @classmethod
    def setUpClass(cls):
        cls.media_dir = tempfile.mkdtemp(prefix='bandhu-test-media-')
        cls._media_override = override_settings(MEDIA_ROOT=cls.media_dir)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls.media_dir, ignore_errors=True)
