"""
Seed People page staff and designations for local development.
Run: python manage.py seed_people
"""
import os
import re
import shutil
import urllib.error
import urllib.request
from datetime import date

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bandhuapp.models import Designation, DesignationRole, PeoplesDesignation, Profile, Staff

User = get_user_model()

DEFAULT_DESIGNATIONS = [
    {'title': 'Core Team', 'rank': 1},
    {'title': 'Office Bearers', 'rank': 2},
]

DEFAULT_CORE_TEAM = [
    {
        'first_name': 'Sanjeeb',
        'last_name': 'Mohapatra',
        'profession': 'Senior Solution Data Architect',
        'designation': 'Core Team',
        'rank': 1,
        'gender': 'M',
    },
    {
        'first_name': 'Rajendra',
        'last_name': 'Badapanda',
        'profession': 'Senior software engineer at Amazon, USA',
        'designation': 'Core Team',
        'rank': 2,
        'gender': 'M',
    },
    {
        'first_name': 'Tarakanta',
        'last_name': 'Nayak',
        'profession': 'Teacher',
        'designation': 'Core Team',
        'rank': 3,
        'gender': 'M',
    },
    {
        'first_name': 'Sarat',
        'last_name': 'Chandra Ghadei',
        'profession': 'Govt Servant',
        'designation': 'Core Team',
        'rank': 4,
        'gender': 'M',
    },
    {
        'first_name': 'Sudhanshu',
        'last_name': 'Mohan Rout',
        'profession': 'Service',
        'designation': 'Core Team',
        'rank': 5,
        'gender': 'M',
    },
    {
        'first_name': 'Susanta',
        'last_name': 'Mallick',
        'profession': 'Service',
        'designation': 'Core Team',
        'rank': 6,
        'gender': 'M',
    },
    {
        'first_name': 'Sraban',
        'last_name': 'Mohanty',
        'profession': 'Professor',
        'designation': 'Core Team',
        'rank': 7,
        'gender': 'M',
    },
    {
        'first_name': 'Sanjaya',
        'last_name': 'Kumar Swain',
        'profession': 'Insurance advisor',
        'designation': 'Core Team',
        'rank': 8,
        'gender': 'M',
    },
    {
        'first_name': 'Biswakam',
        'last_name': 'Mishra',
        'profession': 'IT Professional',
        'designation': 'Core Team',
        'rank': 9,
        'gender': 'M',
    },
]

DEFAULT_OFFICE_BEARER_ROLES = [
    ("President", 1),
    ("Secretary", 2),
    ("Joint Secretary (Programmes)", 3),
    ("Treasurer", 4),
    ("Joint Secretary (Social media, Outreach and Website)", 5),
]

DEFAULT_OFFICE_BEARERS = [
    {
        'first_name': 'Binod',
        'last_name': 'Kumar Sahoo',
        'role': 'President',
        'profession': 'Academic administrator',
        'designation': 'Office Bearers',
        'rank': 1,
        'gender': 'M',
    },
    {
        'first_name': 'Priyabrat',
        'last_name': 'Gochhayat',
        'role': 'Secretary',
        'profession': 'Faculty member',
        'designation': 'Office Bearers',
        'rank': 2,
        'gender': 'M',
    },
    {
        'first_name': 'Mukesh',
        'last_name': 'Dhanuka',
        'role': 'Joint Secretary (Programmes)',
        'profession': 'Teacher',
        'designation': 'Office Bearers',
        'rank': 3,
        'gender': 'M',
    },
    {
        'first_name': 'Subash',
        'last_name': 'Chandra Martha',
        'role': 'Treasurer',
        'profession': 'Faculty member',
        'designation': 'Office Bearers',
        'rank': 4,
        'gender': 'M',
    },
    {
        'first_name': 'Ranjan',
        'last_name': 'Biswal',
        'role': 'Joint Secretary (Social media, Outreach and Website)',
        'profession': 'IT Professional',
        'designation': 'Office Bearers',
        'rank': 5,
        'gender': 'M',
    },
]

DEFAULT_PEOPLE = DEFAULT_CORE_TEAM + DEFAULT_OFFICE_BEARERS

LIVE_PROFILE_PHOTOS = {
    'sanjeeb mohapatra': 'IMG_20230703_211022_Xf7RxXY.jpg',
    'rajendra badapanda': 'image.png',
    'tarakanta nayak': 'photo-gian-tk.jpg',
    'sarat chandra ghadei': 'man.png',
    'sraban mohanty': 'sraban-sir.jpg',
    'biswakam mishra': 'Biswakam_PP.jpg',
    'binod kumar sahoo': 'man.png',
    'priyabrat gochhayat': 'man.png',
    'mukesh dhanuka': 'man.png',
    'subash chandra martha': 'man.png',
    'ranjan biswal': 'Biswa.png',
}

DEFAULT_PROFILE = {
    'dob': date(1980, 1, 1),
    'contact_no': '9000000000',
    'street_address1': 'Bandhu Office',
    'street_address2': '',
    'city': 'Jagatsinghpur',
    'state': 'Odisha',
    'pincode': '754134',
}

LIVE_PEOPLE_URL = 'https://bandhuodisha.in/people/'
LIVE_MEDIA_BASE = 'https://bandhuodisha.in/media/profile_photos/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
LIVE_CARD_PATTERN = re.compile(
    r'<img src="(?P<img>/media/profile_photos/[^"]*)"[^>]*>\s*'
    r'<h5 class="my-2">(?P<name>[^<]+)</h5>\s*'
    r'<p class="text-muted mb-1">(?P<profession>[^<]*)</p>\s*'
    r'<p class="text-muted mb-4">(?P<designation>[^<]*)</p>',
    re.S,
)


def _fetch_live_people_cards():
    request = urllib.request.Request(LIVE_PEOPLE_URL, headers={'User-Agent': USER_AGENT})
    try:
        html = urllib.request.urlopen(request, timeout=30).read().decode('utf-8', 'replace')
    except (urllib.error.URLError, OSError):
        return []

    seen = set()
    cards = []
    for match in LIVE_CARD_PATTERN.finditer(html):
        name = re.sub(r'\s+', ' ', match.group('name').strip())
        key = (_normalize_name(name), match.group('designation').strip())
        if key in seen:
            continue
        seen.add(key)
        cards.append(
            {
                'name': name,
                'profession': match.group('profession').strip(),
                'designation': match.group('designation').strip(),
                'photo': match.group('img').replace('/media/', '', 1),
            }
        )
    return cards


def _apply_live_people_cards(cards, designation_by_title, stdout=None):
    if not cards:
        return 0

    updated = 0
    for card in cards:
        designation = designation_by_title.get(card['designation'])
        if not designation:
            continue

        parts = card['name'].split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''
        email = _email_for_person(first_name, last_name)
        profile = Profile.objects.filter(user__email=email).first()
        if not profile:
            continue

        changed = False
        if card['profession'] and profile.profession != card['profession']:
            profile.profession = card['profession']
            changed = True
        if card['photo'] and (profile.profile_pic.name or '') != card['photo']:
            profile.profile_pic = card['photo']
            changed = True
        if changed:
            profile.save()
            updated += 1
            if stdout:
                stdout.write(f'Updated live profile data for {profile.get_full_name}')

        staff = Staff.objects.filter(profile=profile).first()
        if not staff:
            continue
        peoples_designation, created = PeoplesDesignation.objects.get_or_create(
            staff=staff,
            designation=designation,
            defaults={'desc': card.get('profession', '')},
        )
        if created:
            updated += 1
    return updated



def _email_for_person(first_name, last_name):
    slug = f'{first_name}.{last_name}'.lower().replace(' ', '.')
    return f'{slug}@bandhu.demo'


def _normalize_name(name):
    return re.sub(r'\s+', ' ', (name or '').strip().lower())


def _profile_photo_dir(media_root):
    return os.path.join(media_root, 'profile_photos')


def _ensure_placeholder(media_root, filename):
    dest = os.path.join(_profile_photo_dir(media_root), filename)
    if os.path.isfile(dest):
        return dest

    source = os.path.join(settings.BASE_DIR, 'img', filename)
    if not os.path.isfile(source):
        return None

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(source, dest)
    return dest


def _download_profile_photo(media_root, filename):
    dest = os.path.join(_profile_photo_dir(media_root), filename)
    if os.path.isfile(dest):
        return dest

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    request = urllib.request.Request(
        f'{LIVE_MEDIA_BASE}{filename}',
        headers={'User-Agent': USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(dest, 'wb') as handle:
                handle.write(response.read())
    except (urllib.error.URLError, OSError):
        return None
    return dest if os.path.isfile(dest) else None


def _resolve_profile_photo(media_root, profile):
    current_name = getattr(profile.profile_pic, 'name', '') or ''
    if current_name:
        current_path = os.path.join(media_root, current_name)
        if os.path.isfile(current_path):
            return current_name

        basename = os.path.basename(current_name)
        if basename and _download_profile_photo(media_root, basename):
            return f'profile_photos/{basename}'

    mapped = LIVE_PROFILE_PHOTOS.get(_normalize_name(profile.get_full_name))
    if mapped and _download_profile_photo(media_root, mapped):
        return f'profile_photos/{mapped}'

    placeholder = 'woman.png' if profile.gender == 'F' else 'man.png'
    if _ensure_placeholder(media_root, placeholder):
        return f'profile_photos/{placeholder}'
    return ''


def sync_profile_pictures(stdout=None):
    media_root = settings.MEDIA_ROOT
    updated = 0
    for profile in Profile.objects.filter(staff__isnull=False).select_related('staff'):
        photo_name = _resolve_profile_photo(media_root, profile)
        if not photo_name:
            continue
        if profile.profile_pic.name != photo_name:
            profile.profile_pic = photo_name
            profile.save(update_fields=['profile_pic'])
            updated += 1
            if stdout:
                stdout.write(f'Updated profile photo for {profile.get_full_name} -> {photo_name}')
    return updated


class Command(BaseCommand):
    help = 'Seeds People page staff and designations.'

    def handle(self, *args, **options):
        designation_by_title = {}
        for item in DEFAULT_DESIGNATIONS:
            designation, _created = Designation.objects.get_or_create(
                title=item['title'],
                defaults={'rank': item['rank']},
            )
            designation.rank = item['rank']
            designation.save(update_fields=['rank'])
            designation_by_title[item['title']] = designation

        role_by_title = {}
        office_bearers = designation_by_title.get('Office Bearers')
        if office_bearers:
            for role_title, rank in DEFAULT_OFFICE_BEARER_ROLES:
                role, _created = DesignationRole.objects.get_or_create(
                    designation=office_bearers,
                    title=role_title,
                    defaults={'rank': rank},
                )
                role.rank = rank
                role.save(update_fields=['rank'])
                role_by_title[role_title] = role

        kept_staff_ids = []
        for person in DEFAULT_PEOPLE:
            email = _email_for_person(person['first_name'], person['last_name'])
            user, created = User.objects.get_or_create(email=email)
            if created:
                user.set_password('changeme123')
                user.is_active = True
                user.save()

            profile, _created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': person['first_name'],
                    'last_name': person['last_name'],
                    'gender': person['gender'],
                    'profession': person['profession'],
                    **DEFAULT_PROFILE,
                },
            )
            profile.first_name = person['first_name']
            profile.last_name = person['last_name']
            profile.gender = person['gender']
            profile.profession = person['profession']
            for field, value in DEFAULT_PROFILE.items():
                setattr(profile, field, value)
            profile.save()

            staff, _created = Staff.objects.get_or_create(
                profile=profile,
                defaults={'about': person['profession']},
            )
            staff.about = person['profession']
            staff.save(update_fields=['about'])

            designation_titles = person.get('designations') or [person['designation']]
            for title in designation_titles:
                designation = designation_by_title[title]
                role = None
                if person.get('role') and title in ('Office Bearers', 'Other'):
                    role = role_by_title.get(person['role'])
                peoples_designation, _created = PeoplesDesignation.objects.get_or_create(
                    staff=staff,
                    designation=designation,
                    role=role,
                    defaults={
                        'desc': person['profession'],
                        'rank': person['rank'],
                    },
                )
                peoples_designation.desc = person['profession']
                peoples_designation.rank = person['rank']
                peoples_designation.role = role
                peoples_designation.save()

            kept_staff_ids.append(staff.id)

        demo_emails = {
            _email_for_person(person['first_name'], person['last_name'])
            for person in DEFAULT_PEOPLE
        }
        PeoplesDesignation.objects.filter(
            staff__profile__user__email__in=demo_emails,
        ).exclude(staff_id__in=kept_staff_ids).delete()
        Staff.objects.filter(
            profile__user__email__in=demo_emails,
        ).exclude(id__in=kept_staff_ids).delete()

        updated = sync_profile_pictures(stdout=self.stdout)
        live_updates = _apply_live_people_cards(
            _fetch_live_people_cards(),
            designation_by_title,
            stdout=self.stdout,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'People page updated with {len(kept_staff_ids)} staff member(s); '
                f'synced {updated} profile photo(s); applied {live_updates} live update(s).'
            )
        )
