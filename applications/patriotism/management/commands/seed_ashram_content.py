from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Deprecated. Use seed_patriotism_content instead (no Bandhughar import).'

    def handle(self, *args, **options):
        from django.core.management import call_command
        call_command('seed_patriotism_content', clear=options.get('clear', False))

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true')
