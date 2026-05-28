# Publication file uploads (same as report files for Publications tab)

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0004_add_dummy_visitors_publications'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnkurayanPublicationFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='ankurayan/publications/%Y')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ankurayan', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='publication_files', to='ankurayan.ankurayan')),
            ],
            options={
                'verbose_name': 'Publication file',
                'verbose_name_plural': 'Publication files',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
