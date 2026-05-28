# Data migration: add dummy quotes to existing guests (by name match)

from django.db import migrations

GUEST_QUOTES = {
    'Dr. Meera Patnaik': "The energy and creativity of the participants was inspiring. Bandhu's focus on values and skills together is what our youth need.",
    'Shri Rajesh Kumar': "A well-organised event that brought villages and towns together. The cultural programmes and competitions reflected true community spirit.",
    'Prof. Anita Das': "Spent the day as a judge for the activities. The level of preparation and the warmth of the volunteers made it a memorable visit.",
    'Suresh Patnaik': "Many families visited to support participants and expressed gratitude for the platform Ankurayan provides. Grateful to have been part of it.",
}


def set_quotes(apps, schema_editor):
    Guest = apps.get_model('ankurayan', 'Guest')
    for guest in Guest.objects.all():
        if not guest.quote and guest.name in GUEST_QUOTES:
            guest.quote = GUEST_QUOTES[guest.name]
            guest.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0007_guest_quote'),
    ]

    operations = [
        migrations.RunPython(set_quotes, noop),
    ]
