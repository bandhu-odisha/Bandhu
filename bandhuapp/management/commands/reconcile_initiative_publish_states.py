"""
Reconcile each initiative program's `is_published` flags with their actual content.

`reconcile_publish_states` (bandhuapp/initiative_program_year.py) used to run on
every GET of the home page, a program's list page, and its year-detail page —
paying up to 6 EXISTS queries per year entry on every anonymous visit. The
read paths are now read-only; writes that add content already call
`maybe_publish_entry`, and writes that remove content (deleting a report file,
report link, or invitation letter) call `reconcile_publish_states` directly.
Run this command to catch anything else that could drift the flag — e.g. a
Django-admin edit that clears `reports` text or manually toggles `is_published`.

Run: python manage.py reconcile_initiative_publish_states
"""
from django.core.management.base import BaseCommand

from bandhuapp.initiative_program_year import PROGRAMS, reconcile_publish_states


class Command(BaseCommand):
    help = "Reconcile each initiative program's Ashram.is_published flags with their content."

    def handle(self, *args, **options):
        from applications import patriotism, prasantaraktadan, sevavrata

        program_models = {
            'patriotism': patriotism.models,
            'prasantaraktadan': prasantaraktadan.models,
            'sevavrata': sevavrata.models,
        }
        for program_key in PROGRAMS:
            models = program_models.get(program_key)
            if models is None:
                continue
            before = set(
                models.Ashram.objects.filter(is_published=True).values_list('pk', flat=True)
            )
            reconcile_publish_states(models)
            after = set(
                models.Ashram.objects.filter(is_published=True).values_list('pk', flat=True)
            )
            self.stdout.write(
                f'{program_key}: published {len(after - before)}, '
                f'unpublished {len(before - after)}, unchanged {len(before & after)}.'
            )

        self.stdout.write(self.style.SUCCESS('Done.'))
