"""
Seed notice-board entries for the landing page.
Run: python manage.py seed_landing_notices
"""
from datetime import date

from django.core.management.base import BaseCommand

from bandhuapp.models import RecentActivity
from bandhuapp.notice_links import resolve_notice_url

DEFAULT_NOTICES = [
    {
        'title': 'Ankurayan 2025',
        'description': 'Ankurayan 2025 will be celebrated from 17-Dec to 19-Dec-25.',
        'start_date': date(2025, 12, 17),
        'end_date': date(2025, 12, 19),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Ankurayan 2024 Logo Inauguration',
        'description': 'Inauguration of Ankurayan 2024 Logo will be on 17-Nov-2024 at 10AM.',
        'start_date': date(2024, 11, 17),
        'end_date': None,
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Blood Donation Camp',
        'description': 'Community blood donation drive organised by Bandhu.',
        'start_date': date(2025, 4, 27),
        'end_date': None,
        'link': 'https://tinyurl.com/BandhuBloodDonation',
    },
    {
        'title': 'Patriotism In Action 2024',
        'description': (
            'Date of examination: 23 September 2024. One-day Personality Development camp '
            'and certificate distribution: 2 October 2024.'
        ),
        'start_date': date(2024, 8, 21),
        'end_date': date(2024, 9, 17),
        'link': 'https://forms.gle/NTe28iL8DJHWZPSr6',
    },
    {
        'title': 'Registration for Ankurayan 2024',
        'description': 'Registration form will be open from 17-Nov-2024 2 PM till 12-Dec-2024 11:50PM.',
        'start_date': date(2024, 11, 17),
        'end_date': date(2024, 12, 12),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Ankurayan 2023',
        'description': (
            'Ankurayan, festival of emerging minds and dreaming children will be celebrated '
            'from 17 to 19 Dec 23.'
        ),
        'start_date': date(2023, 12, 17),
        'end_date': date(2023, 12, 19),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Registration for Ankurayan 2023',
        'description': 'Registration form will be available online from 25-Nov to 13-Dec-23.',
        'start_date': date(2023, 11, 25),
        'end_date': date(2023, 12, 13),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Patriotism in Action 2023',
        'description': 'Click Here for details about "Patriotism in Action 2023".',
        'start_date': date(2023, 8, 15),
        'end_date': date(2023, 10, 2),
        'link': 'https://bandhuodisha.in/other_activities/',
    },
    {
        'title': 'General Council Meeting',
        'description': 'General Council Meeting will be held on 13 Nov 2022, Sunday at Bandhughara, Lankapada.',
        'start_date': date(2022, 11, 13),
        'end_date': None,
        'link': 'https://bandhuodisha.in/',
    },
    {
        'title': 'Registration for Ankurayan 2022',
        'description': 'Registration form will be available online from 26-Nov to 14-Dec-22.',
        'start_date': date(2022, 11, 26),
        'end_date': date(2022, 12, 14),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Ankurayan 2022',
        'description': (
            'Ankurayan (ଅଙ୍କୁରାୟନ), Festival for emerging minds and dreaming children will be '
            'celebrated from 17 to 19-Dec-22.'
        ),
        'start_date': date(2022, 12, 17),
        'end_date': date(2022, 12, 19),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'Patriotism In Action',
        'description': 'Celebration Day: 02 October 2022.',
        'start_date': date(2022, 9, 3),
        'end_date': date(2022, 10, 2),
        'link': 'https://bandhuodisha.in/other_activities/',
    },
    {
        'title': 'Ankurayan 2021',
        'description': 'Festival for emerging minds and dreaming children will be celebrated from 17 to 19-Dec-21.',
        'start_date': date(2021, 12, 17),
        'end_date': date(2021, 12, 19),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
    {
        'title': 'General Council Meeting',
        'description': (
            'Bandhu General Council Meeting will be held on 14 Nov 2021 (Sunday) 9 AM to 4 PM, '
            'at Bandhughara, Lankapada.'
        ),
        'start_date': date(2021, 11, 14),
        'end_date': None,
        'link': 'https://bandhuodisha.in/',
    },
    {
        'title': 'General Council Meeting',
        'description': (
            'Bandhu General Council Meeting will be held on 4th April 2021, 9 AM (Sunday), '
            'at Bandhughara, Lankapada.'
        ),
        'start_date': date(2021, 4, 4),
        'end_date': None,
        'link': 'https://bandhuodisha.in/',
    },
    {
        'title': 'Ankurayan 2020',
        'description': 'Ankurayan is a three day festival of light and delight primarily meant for rural children.',
        'start_date': date(2020, 12, 16),
        'end_date': date(2020, 12, 18),
        'link': 'https://bandhuodisha.in/ankurayan/',
    },
]


class Command(BaseCommand):
    help = 'Seeds notice-board entries for the landing page.'

    def handle(self, *args, **options):
        RecentActivity.objects.filter(description__startswith='Notice file:').delete()

        kept_ids = []
        for notice in DEFAULT_NOTICES:
            activity = RecentActivity.objects.filter(
                title=notice['title'],
                start_date=notice['start_date'],
            ).first()
            if not activity:
                activity = RecentActivity(title=notice['title'])
            activity.description = notice['description']
            activity.start_date = notice['start_date']
            activity.end_date = notice['end_date']
            activity.link = resolve_notice_url(
                f"{notice['title']} {notice['description']}", notice['link']
            )
            activity.save()
            kept_ids.append(activity.id)

        RecentActivity.objects.exclude(id__in=kept_ids).delete()
        self.stdout.write(self.style.SUCCESS(f'Notice board updated with {len(kept_ids)} entries.'))
