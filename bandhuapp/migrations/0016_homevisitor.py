from django.db import migrations, models


DEFAULT_VISITORS = [
    {
        'sort_order': 0,
        'name': 'Priya Sharma',
        'occupation': 'Social Worker',
        'place': 'Bhubaneswar',
        'avatar': 'woman',
        'about': (
            'Working with communities for over a decade. Visiting Bandhu reinforced my '
            'belief in dignity-based development.'
        ),
        'quote': (
            'Visiting Bandhu was a deeply moving experience. The warmth and dedication of '
            'everyone here reminded me what community truly means. I left with a renewed sense of hope.'
        ),
        'linkedin_url': 'https://linkedin.com/in/example',
    },
    {
        'sort_order': 1,
        'name': 'Dr. Rajesh Mohanty',
        'occupation': 'Educationist',
        'place': 'Cuttack',
        'avatar': 'man',
        'about': (
            "Faculty in education. Inspired by Bandhu's approach to nurturing values and "
            'self-worth among youth.'
        ),
        'quote': (
            "I came to understand Bandhu's work in villages and cities. The focus on dignity "
            'and self-worth, rather than charity, is what makes this organisation special. Truly inspiring.'
        ),
    },
    {
        'sort_order': 2,
        'name': 'Anita Das',
        'occupation': 'Community Volunteer',
        'place': 'Puri',
        'avatar': 'woman',
        'about': (
            'Volunteer and advocate for rural development. My day at Bandhughar was a reminder '
            'of what partnership can achieve.'
        ),
        'quote': (
            'Spent a day at Bandhughar and saw how they support people as equal partners. '
            'The environment is peaceful and purposeful. I recommend anyone to visit and see for themselves.'
        ),
        'facebook_url': 'https://facebook.com/example',
    },
    {
        'sort_order': 3,
        'name': 'Suresh Patnaik',
        'occupation': 'Development Consultant',
        'place': 'Berhampur',
        'avatar': 'man',
        'about': (
            'Consultant in development sector. Grateful to have met the team and heard stories from the ground.'
        ),
        'quote': (
            "Bandhu doesn't just talk about change—they live it. Meeting the team and hearing stories "
            'from the ground was humbling. Grateful to have shared this experience.'
        ),
    },
]


def seed_home_visitors(apps, schema_editor):
    HomeVisitor = apps.get_model('bandhuapp', 'HomeVisitor')
    if HomeVisitor.objects.exists():
        return
    for row in DEFAULT_VISITORS:
        HomeVisitor.objects.create(**row)


def unseed_home_visitors(apps, schema_editor):
    HomeVisitor = apps.get_model('bandhuapp', 'HomeVisitor')
    names = [row['name'] for row in DEFAULT_VISITORS]
    HomeVisitor.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('bandhuapp', '0015_seed_office_bearer_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='HomeVisitor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('occupation', models.CharField(help_text='Shown as profession in the profile popup.', max_length=100)),
                ('place', models.CharField(help_text='City or region, e.g. Bhubaneswar.', max_length=100)),
                ('avatar', models.CharField(choices=[('man', 'Man (default illustration)'), ('woman', 'Woman (default illustration)')], default='man', max_length=10)),
                ('about', models.TextField(blank=True, default='', max_length=1000)),
                ('quote', models.TextField(max_length=500)),
                ('facebook_url', models.URLField(blank=True, default='', max_length=255)),
                ('linkedin_url', models.URLField(blank=True, default='', max_length=255)),
                ('photo', models.ImageField(blank=True, help_text='Optional. Leave empty to use the default man/woman illustration.', null=True, upload_to='bandhuapp/visitors')),
                ('sort_order', models.PositiveSmallIntegerField(db_index=True, default=0, help_text='Lower numbers appear first in the carousel.')),
                ('is_published', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Homepage visitor',
                'verbose_name_plural': 'Homepage visitors',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.RunPython(seed_home_visitors, unseed_home_visitors),
    ]
