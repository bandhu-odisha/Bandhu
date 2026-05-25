"""
Apply proper-case formatting to all existing profiles and designation notes.
Run: python manage.py fix_profile_casing
"""
from django.core.management.base import BaseCommand

from bandhuapp.helpers import proper_case
from bandhuapp.models import Designation, DesignationRole, PeoplesDesignation, Profile


class Command(BaseCommand):
    help = 'Capitalise profile and designation text fields (first letter of each word).'

    def handle(self, *args, **options):
        profile_count = 0
        for profile in Profile.objects.iterator():
            changed = False
            for field in Profile.PROFILE_PROPER_CASE_FIELDS:
                value = getattr(profile, field, None)
                if isinstance(value, str) and value.strip():
                    formatted = proper_case(value)
                    if formatted != value:
                        setattr(profile, field, formatted)
                        changed = True
            if changed:
                profile.save(update_fields=list(Profile.PROFILE_PROPER_CASE_FIELDS))
                profile_count += 1

        designation_note_count = 0
        for pd in PeoplesDesignation.objects.exclude(desc='').iterator():
            formatted = proper_case(pd.desc.strip())
            if formatted != pd.desc:
                pd.desc = formatted
                pd.save(update_fields=['desc'])
                designation_note_count += 1

        group_count = 0
        for designation in Designation.objects.iterator():
            formatted = proper_case(designation.title)
            if formatted != designation.title:
                designation.title = formatted
                designation.save(update_fields=['title'])
                group_count += 1

        role_count = 0
        for role in DesignationRole.objects.iterator():
            formatted = proper_case(role.title)
            if formatted != role.title:
                role.title = formatted
                role.save(update_fields=['title'])
                role_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {profile_count} profile(s), {designation_note_count} designation note(s), '
                f'{group_count} group(s), and {role_count} role(s).'
            )
        )
