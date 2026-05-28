# Data migration: add dummy content for visitors and publications

from django.db import migrations


DUMMY_VISITORS = """
<p>Visitors and dignitaries who attended Ankurayan this year shared their experiences:</p>
<ul>
<li><strong>Dr. Meera Patnaik</strong> – Educationist and guest speaker: "The energy and creativity of the participants was inspiring. Bandhu's focus on values and skills together is what our youth need."</li>
<li><strong>Shri Rajesh Kumar</strong> – District official: "A well-organised event that brought villages and towns together. The cultural programmes and competitions reflected true community spirit."</li>
<li><strong>Prof. Anita Das</strong> – University faculty: "Spent the day as a judge for the activities. The level of preparation and the warmth of the volunteers made it a memorable visit."</li>
<li><strong>Parents and guardians</strong> – Many families visited to support participants and expressed gratitude for the platform Ankurayan provides.</li>
</ul>
<p>We thank all visitors for their time and encouragement.</p>
"""

DUMMY_PUBLICATIONS = """
<p>Publications and media coverage related to this year's Ankurayan:</p>
<ul>
<li><strong>Annual Report – Ankurayan {{ year }}</strong> – Summary of events, participants, and outcomes (available on request).</li>
<li><strong>Photo booklet</strong> – Highlights from the opening ceremony, activities, and prize distribution.</li>
<li><strong>Local press</strong> – Coverage in regional newspapers and community bulletins.</li>
<li><strong>Bandhu newsletter</strong> – A dedicated section in our quarterly newsletter featuring stories and feedback from this Ankurayan.</li>
</ul>
<p>For copies or more information, please contact us.</p>
"""


def add_dummy_data(apps, schema_editor):
    Ankurayan = apps.get_model('ankurayan', 'Ankurayan')
    for obj in Ankurayan.objects.all():
        updated = False
        if not obj.visitors or not obj.visitors.strip():
            obj.visitors = DUMMY_VISITORS.strip()
            updated = True
        if not obj.publications or not obj.publications.strip():
            # Replace {{ year }} with actual year
            obj.publications = DUMMY_PUBLICATIONS.strip().replace('{{ year }}', str(obj.year))
            updated = True
        if updated:
            obj.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0003_ankurayanreportfile'),
    ]

    operations = [
        migrations.RunPython(add_dummy_data, noop),
    ]
