"""
Walk every FileField/ImageField on every model and report rows whose file
is missing on disk (DB row present, file gone under MEDIA_ROOT).
Run: python manage.py check_media
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import FileField


class Command(BaseCommand):
    help = 'Report model rows whose FileField/ImageField points at a missing file on disk.'

    def handle(self, *args, **options):
        missing = 0
        checked = 0
        for model in apps.get_models():
            file_fields = [f for f in model._meta.get_fields() if isinstance(f, FileField)]
            if not file_fields:
                continue
            for obj in model._default_manager.all().iterator():
                for field in file_fields:
                    value = getattr(obj, field.name)
                    if not value:
                        continue
                    checked += 1
                    try:
                        exists = value.storage.exists(value.name)
                    except (NotImplementedError, ValueError, OSError):
                        exists = False
                    if not exists:
                        missing += 1
                        self.stdout.write(
                            f'{model._meta.label}.{field.name} pk={obj.pk}: {value.name}'
                        )
        self.stdout.write(
            self.style.SUCCESS(f'Checked {checked} file field value(s), {missing} missing.')
        )
