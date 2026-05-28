# Generated manually for report file uploads

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ankurayan', '0002_add_reports_publications_visitors'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnkurayanReportFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='ankurayan/reports/%Y')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('ankurayan', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='report_files', to='ankurayan.ankurayan')),
            ],
            options={
                'verbose_name': 'Report file',
                'verbose_name_plural': 'Report files',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
