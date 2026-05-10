# Data migration: add dummy Guest records so Our Guests cards show

from django.db import migrations


DUMMY_GUESTS = [
    {
        'name': 'Dr. Meera Patnaik',
        'profession': 'Educationist, Guest Speaker',
        'about': 'Educationist and guest speaker. The energy and creativity of the participants was inspiring.',
        'email': 'meera.patnaik@example.com',
        'contact_no': '9876543210',
    },
    {
        'name': 'Shri Rajesh Kumar',
        'profession': 'District Official',
        'about': 'A well-organised event that brought villages and towns together.',
        'email': 'rajesh.kumar@example.com',
        'contact_no': '9011731529',
    },
    {
        'name': 'Prof. Anita Das',
        'profession': 'University Faculty',
        'about': 'Spent the day as a judge for the activities. The warmth of the volunteers made it memorable.',
        'email': 'anita.das@example.com',
        'contact_no': '8765432109',
    },
    {
        'name': 'Suresh Patnaik',
        'profession': 'Community Leader',
        'about': 'Many families visited to support participants. Grateful for the platform Ankurayan provides.',
        'email': 'suresh.patnaik@example.com',
        'contact_no': '7654321098',
    },
]


def add_dummy_guests(apps, schema_editor):
    Ankurayan = apps.get_model('ankurayan', 'Ankurayan')
    Guest = apps.get_model('ankurayan', 'Guest')
    # Add dummy guests to every Ankurayan that has no guests yet
    for ankurayan in Ankurayan.objects.all():
        if Guest.objects.filter(ankurayan=ankurayan).exists():
            continue
        for g in DUMMY_GUESTS:
            Guest.objects.create(
                ankurayan=ankurayan,
                name=g['name'],
                profession=g['profession'],
                about=g['about'],
                email=g['email'],
                contact_no=g['contact_no'],
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0005_ankurayanpublicationfile'),
    ]

    operations = [
        migrations.RunPython(add_dummy_guests, noop),
    ]
