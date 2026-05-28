"""
Rewrite legacy notice URLs in the database (e.g. bandhuodisha.in/ankurayan/ → year detail).
Run: python manage.py fix_notice_links
"""
from django.core.management.base import BaseCommand

from bandhuapp.models import CurrentUpdates, RecentActivity
from bandhuapp.notice_links import resolve_notice_url


class Command(BaseCommand):
    help = 'Fix Current Updates and Recent Activity links that point at generic Ankurayan pages.'

    def handle(self, *args, **options):
        updated_current = 0
        for row in CurrentUpdates.objects.all():
            resolved = resolve_notice_url(row.desc, row.url)
            if not resolved or resolved == (row.url or '').strip():
                continue
            row.url = resolved[:100]
            row.save(update_fields=['url'])
            updated_current += 1
            self.stdout.write(f'CurrentUpdates: {row.desc[:50]!r} -> {row.url}')

        updated_recent = 0
        for row in RecentActivity.objects.all():
            resolved = resolve_notice_url(f'{row.title} {row.description}', row.link)
            if not resolved or resolved == (row.link or '').strip():
                continue
            row.link = resolved[:500]
            row.save(update_fields=['link'])
            updated_recent += 1
            self.stdout.write(f'RecentActivity: {row.title!r} -> {row.link}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. Updated {updated_current} current update(s), {updated_recent} recent activit(ies).'
            )
        )
