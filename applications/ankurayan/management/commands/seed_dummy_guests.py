"""Add the two example Guest rows for Ankurayan (skips if name already exists for that year)."""

from django.core.management.base import BaseCommand

from applications.ankurayan.guest_examples import EXAMPLE_GUESTS
from applications.ankurayan.models import Ankurayan, Guest


class Command(BaseCommand):
    help = 'Insert the two example Guest records for Ankurayan (skips existing names per year).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Only this Ankurayan year (e.g. 2025).',
        )
        parser.add_argument(
            '--slug',
            type=str,
            default=None,
            help='Only this Ankurayan slug (e.g. ankurayan-2025).',
        )

    def handle(self, *args, **options):
        qs = Ankurayan.objects.all().order_by('-year')
        if options['year'] is not None:
            qs = qs.filter(year=options['year'])
        if options['slug']:
            qs = qs.filter(slug=options['slug'])
        if not qs.exists():
            self.stdout.write(self.style.WARNING('No Ankurayan rows matched. Nothing to do.'))
            return

        created_total = 0
        skipped_total = 0
        for ankurayan in qs:
            for g in EXAMPLE_GUESTS:
                if Guest.objects.filter(ankurayan=ankurayan, name=g['name']).exists():
                    skipped_total += 1
                    continue
                Guest.objects.create(
                    ankurayan=ankurayan,
                    name=g['name'],
                    profession=g['profession'],
                    about=g.get('about') or '',
                    quote=g.get('quote') or '',
                    email=g.get('email') or '',
                    contact_no=g.get('contact_no') or '',
                    facebook_url=g.get('facebook_url', ''),
                    linkedin_url=g.get('linkedin_url', ''),
                    sort_order=g.get('sort_order', 0),
                )
                created_total += 1
                self.stdout.write(f'  + {ankurayan.year}: {g["name"]}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Created {created_total} guest(s), skipped {skipped_total} existing name(s).'
            )
        )
