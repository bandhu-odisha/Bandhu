# Reset guests to two example profiles per Ankurayan year

from django.db import migrations

from applications.ankurayan.guest_examples import EXAMPLE_GUESTS


def reset_example_guests(apps, schema_editor):
    Ankurayan = apps.get_model('ankurayan', 'Ankurayan')
    Guest = apps.get_model('ankurayan', 'Guest')
    Guest.objects.all().delete()
    for ankurayan in Ankurayan.objects.all().order_by('year'):
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


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0011_guest_sort_order_and_guestnote'),
    ]

    operations = [
        migrations.RunPython(reset_example_guests, noop),
    ]
