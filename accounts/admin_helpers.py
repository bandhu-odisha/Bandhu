import re
import uuid

from django.core.exceptions import ValidationError

from .models import User


def normalize_admin_add_email(raw):
    return (raw or '').strip().lower()


def build_placeholder_login_email(first_name='', last_name=''):
    """Unique login address when the member has no email yet."""
    slug = re.sub(r'[^a-z0-9]+', '-', f'{first_name}-{last_name}'.lower()).strip('-') or 'member'
    slug = slug[:40]
    return f'{slug}.{uuid.uuid4().hex[:10]}@member.bandhu.local'


def resolve_admin_created_user_email(
    *,
    entered_email,
    admin_user,
    admin_password,
    first_name='',
    last_name='',
):
    """
    Pick the login email for a member created by an admin.

    - Blank email → generated placeholder.
    - New unique email → use as login.
    - Admin's own email → requires admin password; member still gets a separate login.
    - Another admin's email or any taken email → rejected.
    """
    entered = normalize_admin_add_email(entered_email)
    if not entered:
        return build_placeholder_login_email(first_name, last_name)

    existing = User.objects.filter(email__iexact=entered).first()
    if not existing:
        return entered

    if existing.is_admin or existing.is_staff:
        admin_email = normalize_admin_add_email(getattr(admin_user, 'email', ''))
        if entered == admin_email:
            if not admin_password:
                raise ValidationError(
                    'Enter your admin password to confirm using your email for this member.',
                    code='admin_password_required',
                )
            if not admin_user or not admin_user.check_password(admin_password):
                raise ValidationError(
                    'Incorrect admin password.',
                    code='admin_password_invalid',
                )
            return build_placeholder_login_email(first_name, last_name)

        raise ValidationError(
            'This email belongs to another admin account and cannot be reused.',
        )

    raise ValidationError('A user with this email already exists.')


def apply_admin_created_user_defaults(user):
    """Members added by admin are regular users, never admins."""
    user.is_admin = False
    user.is_staff = False
    user.is_active = True
    user.auth = True
    user.set_unusable_password()
