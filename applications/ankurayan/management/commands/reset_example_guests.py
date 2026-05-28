"""Remove all Ankurayan guests and apply the two example profiles to every year."""

from django.core.management.base import BaseCommand
from django.db import transaction

from applications.ankurayan.guest_examples import EXAMPLE_GUESTS
from applications.ankurayan.models import Ankurayan, Guest


class Command(BaseCommand):
    help = 'Delete all Guest rows and create only the two example guests for each Ankurayan year.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Only reset this Ankurayan year (e.g. 2020).',
        )
        parser.add_argument(
            '--slug',
            type=str,
            default=None,
            help='Only reset this Ankurayan slug (e.g. ankurayan-2020).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        qs = Ankurayan.objects.all().order_by('year')
        if options['year'] is not None:
            qs = qs.filter(year=options['year'])
        if options['slug']:
            qs = qs.filter(slug=options['slug'])
        if not qs.exists():
            self.stdout.write(self.style.WARNING('No Ankurayan rows matched. Nothing to do.'))
            return

        if options['year'] is None and not options['slug']:
            removed = Guest.objects.count()
            Guest.objects.all().delete()
            self.stdout.write(f'Removed {removed} guest profile(s) total.')
        else:
            removed = Guest.objects.filter(ankurayan__in=qs).count()
            Guest.objects.filter(ankurayan__in=qs).delete()
            self.stdout.write(f'Removed {removed} guest profile(s) for selected year(s).')

        created = 0
        for ankurayan in qs:
            for g in EXAMPLE_GUESTS:
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
                created += 1
            self.stdout.write(f'  {ankurayan.year}: {len(EXAMPLE_GUESTS)} example guest(s)')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {created} guest profile(s) across {qs.count()} Ankurayan year(s).'
            )
        )
