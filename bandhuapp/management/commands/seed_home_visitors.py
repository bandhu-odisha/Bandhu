"""
Seed homepage Our Visitors testimonials.
Run: python manage.py seed_home_visitors
"""
from django.core.management.base import BaseCommand

from bandhuapp.models import HomeVisitor

DEFAULT_VISITORS = [
    {
        'sort_order': 0,
        'name': 'Priya Sharma',
        'occupation': 'Social Worker',
        'place': 'Bhubaneswar',
        'avatar': 'woman',
        'about': (
            'Working with communities for over a decade. Visiting Bandhu reinforced my '
            'belief in dignity-based development.'
        ),
        'quote': (
            'Visiting Bandhu was a deeply moving experience. The warmth and dedication of '
            'everyone here reminded me what community truly means. I left with a renewed sense of hope.'
        ),
        'linkedin_url': 'https://linkedin.com/in/example',
    },
    {
        'sort_order': 1,
        'name': 'Dr. Rajesh Mohanty',
        'occupation': 'Educationist',
        'place': 'Cuttack',
        'avatar': 'man',
        'about': (
            "Faculty in education. Inspired by Bandhu's approach to nurturing values and "
            'self-worth among youth.'
        ),
        'quote': (
            "I came to understand Bandhu's work in villages and cities. The focus on dignity "
            'and self-worth, rather than charity, is what makes this organisation special. Truly inspiring.'
        ),
    },
    {
        'sort_order': 2,
        'name': 'Anita Das',
        'occupation': 'Community Volunteer',
        'place': 'Puri',
        'avatar': 'woman',
        'about': (
            'Volunteer and advocate for rural development. My day at Bandhughar was a reminder '
            'of what partnership can achieve.'
        ),
        'quote': (
            'Spent a day at Bandhughar and saw how they support people as equal partners. '
            'The environment is peaceful and purposeful. I recommend anyone to visit and see for themselves.'
        ),
        'facebook_url': 'https://facebook.com/example',
    },
    {
        'sort_order': 3,
        'name': 'Suresh Patnaik',
        'occupation': 'Development Consultant',
        'place': 'Berhampur',
        'avatar': 'man',
        'about': (
            'Consultant in development sector. Grateful to have met the team and heard stories from the ground.'
        ),
        'quote': (
            "Bandhu doesn't just talk about change—they live it. Meeting the team and hearing stories "
            'from the ground was humbling. Grateful to have shared this experience.'
        ),
    },
]


class Command(BaseCommand):
    help = 'Seeds default homepage visitor testimonials (skips if any already exist unless --force).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Replace existing rows with the default set.',
        )

    def handle(self, *args, **options):
        if options['force']:
            HomeVisitor.objects.all().delete()
        elif HomeVisitor.objects.exists():
            self.stdout.write(self.style.WARNING('Homepage visitors already exist; use --force to replace.'))
            return

        for row in DEFAULT_VISITORS:
            HomeVisitor.objects.create(**row)

        self.stdout.write(self.style.SUCCESS(f'Created {len(DEFAULT_VISITORS)} homepage visitors.'))
